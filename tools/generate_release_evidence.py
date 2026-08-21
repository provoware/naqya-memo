#!/usr/bin/env python3
"""Erzeugt einen nachprüfbaren, plattformgebundenen NAQYA-Release-Nachweis."""
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
DIAGNOSTICS_CONTRACT = ROOT / "diagnostics/DIAGNOSTICS_CONTRACT.json"
EXPECTED_DIAGNOSTICS_SHA256 = "fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425"

TARGETS = {
    "linux": {
        "architecture": "x86_64",
        "rust_target": "x86_64-unknown-linux-gnu",
        "package_format": "deb",
        "reproducibility_profile": "dpkg-deb-normalized-v1",
    },
    "windows": {
        "architecture": "x86_64",
        "rust_target": "x86_64-pc-windows-msvc",
        "package_format": "nsis",
        "reproducibility_profile": "tauri-nsis-pinned-v1",
    },
}


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


def detected_rust_target() -> str:
    result = subprocess.run(["rustc", "-vV"], check=True, capture_output=True, text=True, timeout=15)
    for line in result.stdout.splitlines():
        if line.startswith("host: "):
            return line.split(":", 1)[1].strip()
    raise SystemExit("FEHLER: Rust-Zielplattform konnte nicht ermittelt werden.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-os", choices=sorted(TARGETS), required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--sidecar", required=True)
    parser.add_argument("--source-sidecar", required=True)
    parser.add_argument("--runtime-deps", required=True)
    parser.add_argument("--dist-manifest", default="dist/BUILD_MANIFEST.json")
    parser.add_argument("--output", default="release/RELEASE_EVIDENCE.json")
    parser.add_argument("--text-output", default="release/RELEASE_EVIDENCE.txt")
    parser.add_argument("--rust-target")
    parser.add_argument("--package-format", choices=("deb", "nsis"))
    parser.add_argument("--reproducibility-profile")
    parser.add_argument("--sidecar-started", action="store_true")
    parser.add_argument("--dependencies-resolved", action="store_true")
    parser.add_argument(
        "--package-reproducibility-verified",
        "--package-repack-deterministic",
        dest="package_reproducibility_verified",
        action="store_true",
        help="Bestätigt den plattformspezifischen Reproduzierbarkeitsvertrag des Desktop-Pakets.",
    )
    args = parser.parse_args()

    target_profile = TARGETS[args.target_os]
    rust_target = args.rust_target or detected_rust_target()
    package_format = args.package_format or target_profile["package_format"]
    reproducibility_profile = args.reproducibility_profile or target_profile["reproducibility_profile"]

    if rust_target != target_profile["rust_target"]:
        raise SystemExit(
            f"FEHLER: Rust-Ziel {rust_target} passt nicht zu {args.target_os}; erwartet {target_profile['rust_target']}."
        )
    if package_format != target_profile["package_format"]:
        raise SystemExit(
            f"FEHLER: Paketformat {package_format} passt nicht zu {args.target_os}; erwartet {target_profile['package_format']}."
        )
    if reproducibility_profile != target_profile["reproducibility_profile"]:
        raise SystemExit(
            "FEHLER: Reproduzierbarkeitsprofil passt nicht zum freigegebenen Plattformvertrag: "
            f"{reproducibility_profile} != {target_profile['reproducibility_profile']}"
        )

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
        "Diagnosevertrag": DIAGNOSTICS_CONTRACT,
    }.items():
        if not path.is_file():
            raise SystemExit(f"FEHLER: {label} fehlt: {path}")

    if not args.sidecar_started or not args.dependencies_resolved or not args.package_reproducibility_verified:
        raise SystemExit(
            "FEHLER: Release-Nachweis darf erst nach Sidecar-Start, Abhängigkeitsprüfung und bestätigtem Paket-Reproduzierbarkeitsvertrag erzeugt werden."
        )

    version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
    whisper = json.loads((ROOT / "src-tauri/sidecar/whisper-runtime.json").read_text(encoding="utf-8"))
    diagnostics = json.loads(DIAGNOSTICS_CONTRACT.read_text(encoding="utf-8"))
    if diagnostics.get("schema_version") != 1 or diagnostics.get("event_schema_version") != 1:
        raise SystemExit("FEHLER: Nicht unterstützter Diagnosevertrag.")
    if diagnostics.get("format") != "NAQYA-DIAGNOSTICS":
        raise SystemExit("FEHLER: Diagnoseformat stimmt nicht mit dem Releasevertrag überein.")

    diagnostics_contract_sha256 = sha256_file(DIAGNOSTICS_CONTRACT)
    if diagnostics_contract_sha256 != EXPECTED_DIAGNOSTICS_SHA256:
        raise SystemExit(
            "FEHLER: Diagnosevertrag wurde innerhalb 0.5.1-D verändert. "
            f"Erwartet {EXPECTED_DIAGNOSTICS_SHA256}, erhalten {diagnostics_contract_sha256}."
        )

    commit = git_commit()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit(f"FEHLER: Ungültiger Quellcommit: {commit}")

    source_hash = sha256_file(source_sidecar)
    packaged_hash = sha256_file(sidecar)
    if source_hash != packaged_hash:
        raise SystemExit("FEHLER: Gepackter Sidecar weicht bytegenau vom validierten Build-Sidecar ab.")

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    dependency_text = deps.read_text(encoding="utf-8", errors="replace")
    validations = {
        "frontend_manifest_verified": True,
        "source_sidecar_sha_matches_packaged": True,
        "packaged_sidecar_started": True,
        "runtime_dependencies_resolved": True,
        "package_reproducibility_verified": True,
        "diagnostics_contract_bound": True,
    }
    if args.target_os == "linux":
        validations["package_repack_deterministic"] = True

    toolchain = {
        "rustc": command_version("rustc", "--version"),
        "cargo": command_version("cargo", "--version"),
        "cmake": command_version("cmake", "--version"),
        "tauri_cli": command_version("cargo", "tauri", "--version"),
    }
    if args.target_os == "linux":
        toolchain["cc"] = command_version("cc", "--version")
        toolchain["dpkg_deb"] = command_version("dpkg-deb", "--version")
    else:
        toolchain["msvc_cl"] = command_version("cl")
        toolchain["package_tool"] = "tauri-nsis"

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
            "os": args.target_os,
            "architecture": target_profile["architecture"],
            "rust_target": rust_target,
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
            "format": package_format,
            "bytes": package.stat().st_size,
            "sha256": sha256_file(package),
            "reproducibility_profile": reproducibility_profile,
            "source_date_epoch": int(os.environ.get("SOURCE_DATE_EPOCH", "946684800")),
        },
        "runtime_dependencies": {
            "report_file": deps.name,
            "report_sha256": sha256_file(deps),
            "lines": [line for line in dependency_text.splitlines() if line.strip()],
        },
        "diagnostics_contract": {
            "file": "diagnostics/DIAGNOSTICS_CONTRACT.json",
            "schema_version": diagnostics["schema_version"],
            "event_schema_version": diagnostics["event_schema_version"],
            "format": diagnostics["format"],
            "sha256": diagnostics_contract_sha256,
        },
        "toolchain": toolchain,
        "ci": {
            "provider": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "lokal",
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
        },
        "validations": validations,
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    platform_name = "Linux" if args.target_os == "linux" else "Windows"
    text_output = ROOT / args.text_output
    text_output.write_text(
        "NAQYA RELEASE-NACHWEIS\n"
        f"Was: {platform_name}-Desktop-Paket {package.name}\n"
        f"Wann: {generated_at}\n"
        f"Wo: Git-Commit {commit}, Ziel {rust_target}\n"
        "Wie: deterministisches Frontend-Staging, reproduzierbarer whisper.cpp-Sidecar, Tauri-Bundle, "
        f"Paketprofil {reproducibility_profile}, Paketstart- und Abhängigkeitsprüfung\n"
        f"Sidecar: {packaged_hash} ({sidecar.stat().st_size} Bytes)\n"
        f"Paket: {evidence['desktop_package']['sha256']} ({package.stat().st_size} Bytes)\n"
        f"Diagnosevertrag: {diagnostics_contract_sha256} (Schema {diagnostics['schema_version']}, Ereignisschema {diagnostics['event_schema_version']})\n"
        f"Reproduzierbarkeit: {reproducibility_profile}\n"
        "Ergebnis: BUNDLE-VALIDIERT\n",
        encoding="utf-8",
    )
    print(f"NAQYA {platform_name}-Release-Nachweis: PASS -> {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
