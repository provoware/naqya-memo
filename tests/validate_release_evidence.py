#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "release/RELEASE_EVIDENCE.schema.json"
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


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def validate_schema_contract() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["title"] == "NAQYA Release Evidence"
    for key in ("desktop_package", "whisper", "diagnostics_contract", "evidence_fingerprint", "validations"):
        assert key in schema["required"]


def main() -> None:
    validate_schema_contract()
    if "--schema-only" in sys.argv:
        print("NAQYA Release-Nachweis-Schema: PASS")
        return

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "release/RELEASE_EVIDENCE.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    assert evidence["schema_version"] == 1
    assert evidence["status"] == "bundle-validated"
    datetime.fromisoformat(evidence["generated_at"].replace("Z", "+00:00"))

    source = evidence["source"]
    assert source["repository"] == "provoware/naqya-memo"
    assert source["naqya_version"] == "0.5.0"
    assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])

    target = evidence["target"]
    assert target["os"] in TARGETS, f"Nicht unterstützte Plattform: {target['os']}"
    profile = TARGETS[target["os"]]
    assert target["architecture"] == profile["architecture"]
    assert target["rust_target"] == profile["rust_target"]

    for key in ("frontend", "whisper", "desktop_package"):
        item = evidence[key]
        hash_key = "manifest_sha256" if key == "frontend" else "sha256"
        assert re.fullmatch(r"[0-9a-f]{64}", item[hash_key]), f"Ungültiger SHA-256 in {key}"

    whisper = evidence["whisper"]
    assert whisper["provider"] == "ggml-org/whisper.cpp"
    assert whisper["tag"] == "v1.9.2"
    assert whisper["commit"] == "306c88f4d1286aec1bf96e544632897886af5501"
    assert whisper["build_profile"] == "cpu-release-static"
    assert whisper["bytes"] > 0

    package = evidence["desktop_package"]
    assert package["bytes"] > 0
    assert package["format"] == profile["package_format"]
    assert package["reproducibility_profile"] == profile["reproducibility_profile"]
    assert package["source_date_epoch"] == 946684800

    diagnostics = evidence["diagnostics_contract"]
    contract = json.loads(DIAGNOSTICS_CONTRACT.read_text(encoding="utf-8"))
    actual_contract_sha = hashlib.sha256(DIAGNOSTICS_CONTRACT.read_bytes()).hexdigest()
    assert actual_contract_sha == EXPECTED_DIAGNOSTICS_SHA256
    assert diagnostics["file"] == "diagnostics/DIAGNOSTICS_CONTRACT.json"
    assert diagnostics["schema_version"] == contract["schema_version"] == 1
    assert diagnostics["event_schema_version"] == contract["event_schema_version"] == 1
    assert diagnostics["format"] == contract["format"] == "NAQYA-DIAGNOSTICS"
    assert diagnostics["sha256"] == EXPECTED_DIAGNOSTICS_SHA256

    codes_sha = sha256_json(contract["codes"])
    expected_inputs = {
        "fingerprint_schema_version": 1,
        "naqya_version": source["naqya_version"],
        "source_commit": source["commit"],
        "whisper_commit": whisper["commit"],
        "diagnostics_contract_sha256": diagnostics["sha256"],
        "diagnostics_schema_version": diagnostics["schema_version"],
        "diagnostics_event_schema_version": diagnostics["event_schema_version"],
        "diagnostic_codes_sha256": codes_sha,
    }
    fingerprint = evidence["evidence_fingerprint"]
    assert fingerprint["schema_version"] == 1
    assert fingerprint["algorithm"] == "sha256"
    assert fingerprint["diagnostic_codes_sha256"] == codes_sha
    assert fingerprint["inputs"] == expected_inputs
    assert fingerprint["sha256"] == sha256_json(expected_inputs)
    assert re.fullmatch(r"[0-9a-f]{64}", fingerprint["sha256"])

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
        assert validations[key] is True, f"Release-Gate nicht erfüllt: {key}"

    assert "2.11.4" in evidence["toolchain"]["tauri_cli"], "Tauri-CLI-Pin stimmt nicht"
    if target["os"] == "linux":
        assert validations["package_repack_deterministic"] is True
        assert "dpkg-deb" in evidence["toolchain"]["dpkg_deb"], "dpkg-deb-Version fehlt"
    else:
        assert evidence["toolchain"]["package_tool"] == "tauri-nsis"

    if os.environ.get("GITHUB_ACTIONS") == "true":
        assert evidence["ci"]["provider"] == "github-actions"
        assert str(evidence["ci"]["run_id"] or "").isdigit()
        assert str(evidence["ci"]["run_number"] or "").isdigit()

    print(
        "NAQYA Release-Nachweis inklusive Plattform-, Paket-, Diagnose- und Fingerprint-Bindung: "
        f"PASS ({target['os']}/{target['rust_target']}, {fingerprint['sha256']})"
    )


if __name__ == "__main__":
    main()
