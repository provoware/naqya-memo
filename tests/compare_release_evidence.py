#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED_DIAGNOSTICS_SHA256 = "fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425"
EXPECTED_WHISPER_COMMIT = "306c88f4d1286aec1bf96e544632897886af5501"


def load(path: str) -> dict:
    file = Path(path)
    if not file.is_file():
        raise SystemExit(f"FEHLER: Evidence-Datei fehlt: {file}")
    return json.loads(file.read_text(encoding="utf-8"))


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Aufruf: compare_release_evidence.py <linux-evidence.json> <windows-evidence.json>")

    linux = load(sys.argv[1])
    windows = load(sys.argv[2])

    assert linux["schema_version"] == windows["schema_version"] == 1
    assert linux["status"] == windows["status"] == "bundle-validated"

    assert linux["target"] == {
        "os": "linux",
        "architecture": "x86_64",
        "rust_target": "x86_64-unknown-linux-gnu",
    }
    assert windows["target"] == {
        "os": "windows",
        "architecture": "x86_64",
        "rust_target": "x86_64-pc-windows-msvc",
    }

    for key in ("repository", "commit", "naqya_version"):
        assert linux["source"][key] == windows["source"][key], f"Quellnachweis driftet: {key}"

    for key in ("provider", "tag", "commit", "build_profile"):
        assert linux["whisper"][key] == windows["whisper"][key], f"Whisper-Provenienz driftet: {key}"
    assert linux["whisper"]["commit"] == EXPECTED_WHISPER_COMMIT

    assert linux["desktop_package"]["format"] == "deb"
    assert linux["desktop_package"]["reproducibility_profile"] == "dpkg-deb-normalized-v1"
    assert windows["desktop_package"]["format"] == "nsis"
    assert windows["desktop_package"]["reproducibility_profile"] == "tauri-nsis-pinned-v1"

    linux_contract = linux["diagnostics_contract"]
    windows_contract = windows["diagnostics_contract"]
    assert linux_contract == windows_contract, "Linux- und Windows-Diagnosevertrag sind nicht identisch gebunden"
    assert linux_contract == {
        "file": "diagnostics/DIAGNOSTICS_CONTRACT.json",
        "schema_version": 1,
        "event_schema_version": 1,
        "format": "NAQYA-DIAGNOSTICS",
        "sha256": EXPECTED_DIAGNOSTICS_SHA256,
    }

    linux_fingerprint = linux["evidence_fingerprint"]
    windows_fingerprint = windows["evidence_fingerprint"]
    assert linux_fingerprint == windows_fingerprint, (
        "Linux und Windows besitzen nicht denselben Evidence-Fingerprint; gemeinsame Vertragsdaten driften"
    )
    assert linux_fingerprint["schema_version"] == 1
    assert linux_fingerprint["algorithm"] == "sha256"
    assert linux_fingerprint["inputs"]["source_commit"] == linux["source"]["commit"]
    assert linux_fingerprint["inputs"]["naqya_version"] == linux["source"]["naqya_version"]
    assert linux_fingerprint["inputs"]["whisper_commit"] == EXPECTED_WHISPER_COMMIT
    assert linux_fingerprint["inputs"]["diagnostics_contract_sha256"] == EXPECTED_DIAGNOSTICS_SHA256

    for evidence, platform in ((linux, "linux"), (windows, "windows")):
        validations = evidence["validations"]
        for key in (
            "frontend_manifest_verified",
            "source_sidecar_sha_matches_packaged",
            "packaged_sidecar_started",
            "runtime_dependencies_resolved",
            "package_reproducibility_verified",
            "diagnostics_contract_bound",
            "evidence_fingerprint_verified",
        ):
            assert validations[key] is True, f"{platform}: Gate nicht erfüllt: {key}"

    print(
        "NAQYA Linux/Windows-Evidence-Paar: PASS – gleicher Quellstand, gleiche whisper.cpp-Provenienz, "
        f"gleicher Diagnosevertrag und Evidence-Fingerprint {linux_fingerprint['sha256']}"
    )


if __name__ == "__main__":
    main()
