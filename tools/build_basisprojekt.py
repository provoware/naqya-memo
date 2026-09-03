#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "manifeste" / "MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json"
PRODUCT_BASELINE = ROOT / "registry" / "PRODUCT_BASELINE.json"
VERSION = ROOT / "registry" / "VERSION.json"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class BuildError(RuntimeError):
    pass


def load_json(path: Path, label: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BuildError(f"{label} ist nicht lesbar: {exc}") from exc
    if not isinstance(data, dict):
        raise BuildError(f"{label} besitzt kein JSON-Objekt.")
    return data


def load_contract() -> dict:
    data = load_json(CONTRACT, "Basisprojekt-Manifest")
    if data.get("schema_version") != 1 or data.get("status") != "AKTIV":
        raise BuildError("Basisprojekt-Manifest besitzt keinen aktiven Schema-v1-Vertrag.")
    return data


def load_product_baseline() -> dict:
    data = load_json(PRODUCT_BASELINE, "Produkt-Baseline")
    if data.get("product_id") != "naqya-memo":
        raise BuildError("Produkt-Baseline besitzt eine unerwartete Produktkennung.")
    return data


def excluded(rel: str, patterns: list[str]) -> bool:
    posix = PurePosixPath(rel).as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in patterns)


def reject_link_or_special(path: Path, rel: str, *, kind: str) -> None:
    if path.is_symlink():
        raise BuildError(f"Symlink ist im Basisprojekt nicht zulässig: {rel}")
    if kind == "file":
        if not path.is_file():
            raise BuildError(f"Pflichtdatei fehlt oder ist keine reguläre Datei: {rel}")
    elif kind == "dir":
        if not path.is_dir():
            raise BuildError(f"Freigegebener Basisordner fehlt oder ist kein Verzeichnis: {rel}")
    else:
        raise BuildError(f"Interner Prüffehler für Pfadtyp: {rel}")


def collect_files(contract: dict) -> list[Path]:
    patterns = list(contract["exclude_globs"])
    files: dict[str, Path] = {}

    for name in contract["mandatory_root_files"]:
        path = ROOT / name
        reject_link_or_special(path, name, kind="file")
        files[name] = path

    for rel in contract["include_files"]:
        path = ROOT / rel
        reject_link_or_special(path, rel, kind="file")
        files[PurePosixPath(rel).as_posix()] = path

    for root_name in contract["include_roots"]:
        root = ROOT / root_name
        reject_link_or_special(root, root_name, kind="dir")
        for path in root.rglob("*"):
            rel = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                raise BuildError(f"Symlink ist im Basisprojekt nicht zulässig: {rel}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise BuildError(f"Spezialdatei ist im Basisprojekt nicht zulässig: {rel}")
            if not excluded(rel, patterns):
                files[rel] = path

    for rel in files:
        if excluded(rel, patterns):
            raise BuildError(f"Ausgeschlossene Datei würde exportiert: {rel}")

    return [files[key] for key in sorted(files)]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "UNKNOWN"


def legacy_version() -> str:
    data = load_json(VERSION, "Legacy-Versionsregistry")
    return str(data.get("version") or "UNKNOWN")


def source_identity() -> dict:
    baseline = load_product_baseline()
    legacy = legacy_version()
    expected_legacy = str(baseline.get("legacy_version_contract") or "")
    if not expected_legacy or legacy != expected_legacy:
        raise BuildError(
            f"Versionsdrift: registry/VERSION.json={legacy!r}, "
            f"Produkt-Baseline erwartet {expected_legacy!r}."
        )
    acceptance = baseline.get("acceptance")
    lineage = baseline.get("lineage")
    if not isinstance(acceptance, dict) or not isinstance(lineage, dict):
        raise BuildError("Produkt-Baseline enthält keine vollständige Acceptance-/Lineage-Identität.")
    return {
        "product_version": str(baseline.get("product_version") or "UNKNOWN"),
        "product_revision": str(baseline.get("product_revision") or "UNKNOWN"),
        "ui_contract_version": str(baseline.get("ui_contract_version") or "UNKNOWN"),
        "legacy_version_contract": expected_legacy,
        "acceptance": {
            "track": str(acceptance.get("track") or "UNKNOWN"),
            "revision": str(acceptance.get("revision") or "UNKNOWN"),
        },
        "required_ancestor_sha": str(lineage.get("required_ancestor_sha") or "UNKNOWN"),
    }


def generated_manifest(paths: list[Path], contract: dict) -> dict:
    head = git_head()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise BuildError("Quell-SHA ist nicht verfügbar; Basisprojekt wird fail-closed nicht erzeugt.")
    identity = source_identity()
    rows = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    ]
    return {
        "schema_version": 2,
        "project": contract["project"],
        "artifact_type": "vollstaendiges_basisprojekt",
        "artifact_status": contract["status"],
        "source_git_head": head,
        **identity,
        "file_count": len(rows),
        "files": rows,
    }


def safe_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-") or "UNKNOWN"


def validate_output_dir(outdir: Path, contract: dict) -> Path:
    resolved = outdir.resolve()
    if resolved == ROOT:
        raise BuildError("Ausgabeordner darf nicht der Projektwurzel entsprechen.")
    for root_name in contract["include_roots"]:
        include_root = (ROOT / root_name).resolve()
        if resolved == include_root or resolved.is_relative_to(include_root):
            raise BuildError(
                f"Ausgabeordner liegt in einem exportierten Quellordner: {root_name}"
            )
    return resolved


def write_zip(paths: list[Path], manifest: dict, outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    product = safe_token(manifest["product_version"])
    short_sha = manifest["source_git_head"][:12]
    output = outdir / (
        f"PROVOWARE_Naqya-Memo_BASISPROJEKT_STATUS-AKTIV_"
        f"V{product}_SHA-{short_sha}.zip"
    )
    tmp = output.with_suffix(output.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, ZIP_EPOCH)
            mode = stat.S_IMODE(path.stat().st_mode)
            info.external_attr = ((0o755 if mode & 0o111 else 0o644) & 0xFFFF) << 16
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

        info = zipfile.ZipInfo("BASISPROJEKT_MANIFEST.json", ZIP_EPOCH)
        info.external_attr = (0o644 & 0xFFFF) << 16
        archive.writestr(
            info,
            (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        )

    os.replace(tmp, output)
    return output


def verify_zip(path: Path, manifest: dict) -> None:
    expected = {row["path"]: row for row in manifest["files"]}
    expected["BASISPROJEKT_MANIFEST.json"] = None
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise BuildError("ZIP-Inhalt weicht vom Manifest ab.")
        for rel, row in expected.items():
            if row is None:
                continue
            data = archive.read(rel)
            if len(data) != row["size"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise BuildError(f"Integritätsfehler: {rel}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Erzeugt das saubere vollständige PROVOWARE-Basisprojekt."
    )
    parser.add_argument("--output-dir", default=str(ROOT / "dist"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        contract = load_contract()
        paths = collect_files(contract)
        manifest = generated_manifest(paths, contract)
        if args.check:
            print(
                "PASS basis project contract "
                f"files={len(paths)} product={manifest['product_version']} "
                f"sha={manifest['source_git_head']}"
            )
            return 0

        outdir = validate_output_dir(Path(args.output_dir), contract)
        output = write_zip(paths, manifest, outdir)
        verify_zip(output, manifest)
        print(output)
        print(
            "PASS basis project zip "
            f"files={len(paths)} sha256={sha256_file(output)}"
        )
        return 0
    except BuildError as exc:
        print(f"FEHLER BASISPROJEKT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
