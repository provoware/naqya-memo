#!/usr/bin/env python3
"""Erzeugt einen nachprüfbaren Release-Nachweis aus bereits validierten Buildartefakten."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def command_version(*args: str) -> str:
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=30)
        text = (result.stdout or result.stderr).strip().splitlines()
        return text[0] if text else "unbekannt"
    except Exception as error:
        return f"nicht ermittelbar ({type(error).__name__})"


def git_commit() -> str:
    explicit = os.environ.get("NAQYA_SOURCE_COMMIT", "").strip().lower()
    if explicit:
        return explicit
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip().lower()


def rust_target() -> str:
    result = subprocess.run(["rustc", "-vV"], check=True, capture_output=True, text=True, timeout=15)
    for line in result.stdout.splitlines():
        if line.startswith("host: "):
            return line.split(":", 1)[1].strip()
    raise SystemExit("FEHLER: Rust-Zielplattform konnte nicht ermittelt werden.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--sidecar", required=True)
    parser.add_argument("--source-sidecar", required=True)
    parser.add_argument("--runtime-deps", required=True)
    parser.add_argument("--dist-manifest", default="dist/BUILD_MANIFEST.json")
    parser.add_argument("--output", default="release/RELEASE_EVIDENCE.json")
    parser.add_argument("--text-output", default="release/RELEASE_EVIDENCE.txt")
    parser.add_argument("--sidecar-started", action="store_true")
    parser.add_argument("--dependencies-resolved", action="store_true")
    parser.add_argument("--package-repack-deterministic", action="store_true")
    args = parser.parse_args()

    package = Path(args.package).resolve()
    sidecar = Path(args.sidecar).resolve()
    source_sidecar = Path(args.source_sidecar).resolve()
    deps = Path(args.runtime_deps).resolve()
    dist_manifest = (ROOT / args.dist_manifest).resolve()
    for label, path in {
        "Desktop-Paket": package,
        "gepackter Sidecar": sidecar,
        "Build-Sidecar": source_sidecar,
        "Laufzeitabhängigkeitsbericht": deps,
        "Frontend-Manifest": dist_manifest,
    }.items():
        if not path.is_file():
            raise SystemExit(f"FEHLER: {label} fehlt: {path}")

    if not args.sidecar_started or not args.dependencies_resolved or not args.package_repack_deterministic:
        raise SystemExit(
            "FEHLER: Release-Nachweis darf erst nach Sidecar-Start, Abhängigkeitsprüfung und deterministischem DEB-Repacking erzeugt werden."
        )

    version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
    whisper = json.loads((ROOT / "src-tauri/sidecar/whisper-runtime.json").read_text(encoding="utf-8"))
    commit = git_commit()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit(f"FEHLER: Ungültiger Quellcommit: {commit}")

    source_hash = sha256_file(source_sidecar)
    packaged_hash = sha256_file(sidecar)
    if source_hash != packaged_hash:
        raise SystemExit("FEHLER: Gepackter Sidecar weicht bytegenau vom validierten Build-Sidecar ab.")

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    dependency_text = deps.read_text(encoding="utf-8", errors="replace")
    evidence = {
        "schema_version": 1,
        "status": "bundle-validated",
        "generated_at": generated_at,
        "source": {
            "repository": "provoware/naqya-memo",
            "commit": commit,
            "naqya_version": version["version"],
        },
        "target": {
            "os": "linux",
            "architecture": "x86_64",
            "rust_target": rust_target(),
        },
        "frontend": {
            "manifest_file": dist_manifest.name,
            "manifest_sha256": sha256_file(dist_manifest),
        },
        "whisper": {
            "provider": whisper["provider"],
            "tag": whisper["upstream_tag"],
            "commit": whisper["upstream_commit"],
            "build_profile": whisper["build_profile"],
            "source_file": source_sidecar.name,
            "packaged_file": sidecar.name,
            "bytes": sidecar.stat().st_size,
            "sha256": packaged_hash,
        },
        "desktop_package": {
            "file": package.name,
            "bytes": package.stat().st_size,
            "sha256": sha256_file(package),
            "reproducibility_profile": "dpkg-deb-normalized-v1",
            "source_date_epoch": int(os.environ.get("SOURCE_DATE_EPOCH", "946684800")),
        },
        "runtime_dependencies": {
            "report_file": deps.name,
            "report_sha256": sha256_file(deps),
            "lines": [line for line in dependency_text.splitlines() if line.strip()],
        },
        "toolchain": {
            "rustc": command_version("rustc", "--version"),
            "cargo": command_version("cargo", "--version"),
            "cmake": command_version("cmake", "--version"),
            "tauri_cli": command_version("cargo", "tauri", "--version"),
            "cc": command_version("cc", "--version"),
            "dpkg_deb": command_version("dpkg-deb", "--version"),
        },
        "ci": {
            "provider": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "lokal",
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
        },
        "validations": {
            "frontend_manifest_verified": True,
            "source_sidecar_sha_matches_packaged": True,
            "packaged_sidecar_started": True,
            "runtime_dependencies_resolved": True,
            "package_repack_deterministic": True,
        },
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    text_output = ROOT / args.text_output
    text_output.write_text(
        "NAQYA RELEASE-NACHWEIS\n"
        f"Was: Linux-Desktop-Paket {package.name}\n"
        f"Wann: {generated_at}\n"
        f"Wo: Git-Commit {commit}, Ziel {evidence['target']['rust_target']}\n"
        "Wie: deterministisches Frontend-Staging, statischer whisper.cpp-Sidecar, Tauri-Bundle, deterministisches DEB-Repacking, Paketstart- und Abhängigkeitsprüfung\n"
        f"Sidecar: {packaged_hash} ({sidecar.stat().st_size} Bytes)\n"
        f"Paket: {evidence['desktop_package']['sha256']} ({package.stat().st_size} Bytes)\n"
        "DEB-Reproduzierbarkeit: dpkg-deb-normalized-v1\n"
        "Ergebnis: BUNDLE-VALIDIERT\n",
        encoding="utf-8",
    )
    print(f"NAQYA Release-Nachweis: PASS -> {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
