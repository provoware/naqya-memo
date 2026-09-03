#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "manifeste" / "MANIFEST_BASISPROJEKT__STATUS-AKTIV__V1.0.json"
PRODUCT_BASELINE = ROOT / "registry" / "PRODUCT_BASELINE.json"
VERSION = ROOT / "registry" / "VERSION.json"


class VerifyError(RuntimeError):
    pass


def load_json(path: Path, label: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise VerifyError(f"{label} ist nicht lesbar: {exc}") from exc
    if not isinstance(data, dict):
        raise VerifyError(f"{label} besitzt kein JSON-Objekt.")
    return data


def load_contract() -> dict:
    data = load_json(CONTRACT, "Basisprojekt-Vertrag")
    if data.get("schema_version") != 1 or data.get("status") != "AKTIV":
        raise VerifyError("Basisprojekt-Vertrag ist nicht aktiv oder besitzt ein unbekanntes Schema.")
    return data


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def excluded(name: str, patterns: list[str]) -> bool:
    posix = PurePosixPath(name).as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in patterns)


def require_regular_source(path: Path, rel: str, *, directory: bool = False) -> None:
    if path.is_symlink():
        raise VerifyError(f"Symlink in freigegebener Quelle: {rel}")
    if directory:
        if not path.is_dir():
            raise VerifyError(f"Freigegebener Quellordner fehlt: {rel}")
    elif not path.is_file():
        raise VerifyError(f"Freigegebene Quelldatei fehlt: {rel}")


def expected_source_files(contract: dict) -> dict[str, Path]:
    patterns = list(contract["exclude_globs"])
    files: dict[str, Path] = {}

    for rel in contract["mandatory_root_files"]:
        path = ROOT / rel
        require_regular_source(path, rel)
        if excluded(rel, patterns):
            raise VerifyError(f"Pflichtdatei ist zugleich ausgeschlossen: {rel}")
        files[rel] = path

    for rel in contract["include_files"]:
        path = ROOT / rel
        require_regular_source(path, rel)
        if excluded(rel, patterns):
            raise VerifyError(f"Freigegebene Datei ist zugleich ausgeschlossen: {rel}")
        files[PurePosixPath(rel).as_posix()] = path

    for root_name in contract["include_roots"]:
        root = ROOT / root_name
        require_regular_source(root, root_name, directory=True)
        for path in root.rglob("*"):
            rel = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                raise VerifyError(f"Symlink in freigegebener Quelle: {rel}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise VerifyError(f"Spezialdatei in freigegebener Quelle: {rel}")
            if not excluded(rel, patterns):
                files[rel] = path

    return {key: files[key] for key in sorted(files)}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_identity() -> dict:
    baseline = load_json(PRODUCT_BASELINE, "Produkt-Baseline")
    version = load_json(VERSION, "Legacy-Versionsregistry")
    if baseline.get("product_id") != "naqya-memo":
        raise VerifyError("Produkt-Baseline besitzt eine unerwartete Produktkennung.")
    legacy = str(version.get("version") or "UNKNOWN")
    expected_legacy = str(baseline.get("legacy_version_contract") or "")
    if legacy != expected_legacy:
        raise VerifyError("Legacy-Versionsregistry und Produkt-Baseline sind nicht synchron.")
    acceptance = baseline.get("acceptance")
    lineage = baseline.get("lineage")
    if not isinstance(acceptance, dict) or not isinstance(lineage, dict):
        raise VerifyError("Produkt-Baseline enthält keine vollständige Acceptance-/Lineage-Identität.")
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


def regular_zip_member(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    file_type = stat.S_IFMT(mode)
    return file_type in (0, stat.S_IFREG)


def verify(zip_path: Path, expected_head: str) -> dict:
    contract = load_contract()
    expected_files = expected_source_files(contract)
    identity = source_identity()

    if not zip_path.is_file():
        raise VerifyError(f"ZIP fehlt: {zip_path}")

    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise VerifyError("ZIP enthält doppelte Pfade.")
        if not all(safe_member(name) for name in names):
            raise VerifyError("ZIP enthält unsichere oder absolute Pfade.")
        if not all(regular_zip_member(info) for info in infos):
            raise VerifyError("ZIP enthält Symlink- oder Spezialdatei-Einträge.")

        manifest_name = contract["artifact_policy"]["generated_manifest_name"]
        expected_names = set(expected_files) | {manifest_name}
        if set(names) != expected_names:
            missing = sorted(expected_names - set(names))
            extra = sorted(set(names) - expected_names)
            raise VerifyError(f"ZIP-Dateiliste weicht von der freigegebenen Quelle ab: missing={missing} extra={extra}")

        try:
            manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
        except Exception as exc:
            raise VerifyError(f"Generiertes Manifest ist ungültig: {exc}") from exc

        if manifest.get("schema_version") != 2:
            raise VerifyError("Generiertes Manifest besitzt nicht das erwartete Schema v2.")
        if manifest.get("artifact_type") != "vollstaendiges_basisprojekt":
            raise VerifyError("Falscher Artefakttyp.")
        if manifest.get("artifact_status") != contract.get("status"):
            raise VerifyError("Artefaktstatus stimmt nicht.")
        if manifest.get("project") != contract.get("project"):
            raise VerifyError("Projektkennung stimmt nicht.")

        source_head = str(manifest.get("source_git_head") or "")
        if not re.fullmatch(r"[0-9a-f]{40}", source_head):
            raise VerifyError("source_git_head fehlt oder ist ungültig.")
        if expected_head and source_head != expected_head:
            raise VerifyError(f"SHA-Abweichung: Manifest {source_head}, erwartet {expected_head}.")

        for key, value in identity.items():
            if manifest.get(key) != value:
                raise VerifyError(f"Produkt-/Lineage-Identität weicht ab: {key}")

        rows = manifest.get("files")
        if not isinstance(rows, list) or manifest.get("file_count") != len(rows):
            raise VerifyError("file_count und Dateiliste stimmen nicht überein.")

        indexed: dict[str, dict] = {}
        for row in rows:
            if not isinstance(row, dict):
                raise VerifyError("Ungültiger Manifest-Dateieintrag.")
            rel = str(row.get("path") or "")
            if not safe_member(rel) or rel == manifest_name or rel in indexed:
                raise VerifyError(f"Ungültiger oder doppelter Manifestpfad: {rel!r}")
            indexed[rel] = row

        if set(indexed) != set(expected_files):
            raise VerifyError("Generierte Manifest-Dateiliste ist nicht die freigegebene Quell-Dateiliste.")

        patterns = list(contract.get("exclude_globs") or [])
        for rel, source_path in expected_files.items():
            if excluded(rel, patterns):
                raise VerifyError(f"Ausgeschlossene Datei im Basisprojekt: {rel}")
            data = archive.read(rel)
            source_data = source_path.read_bytes()
            if data != source_data:
                raise VerifyError(f"ZIP-Datei weicht bytegenau von der Quelle ab: {rel}")
            row = indexed[rel]
            digest = sha256_bytes(data)
            if len(data) != row.get("size"):
                raise VerifyError(f"Größenabweichung: {rel}")
            if digest != row.get("sha256"):
                raise VerifyError(f"SHA-256-Abweichung: {rel}")

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifiziert ein vollständiges PROVOWARE-Basisprojekt unabhängig vom Builder."
    )
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--expected-head", default="")
    args = parser.parse_args()

    try:
        manifest = verify(args.zip_path.resolve(), args.expected_head.strip())
        print(
            "PASS verified basis project "
            f"sha={manifest['source_git_head']} "
            f"product={manifest['product_version']} "
            f"files={manifest['file_count']}"
        )
        return 0
    except (VerifyError, zipfile.BadZipFile) as exc:
        print(f"FEHLER BASISPROJEKT-ARTEFAKT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
