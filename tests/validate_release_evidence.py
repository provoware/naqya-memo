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
DIAGNOSTIC_CONTRACT = ROOT / "diagnostics/DIAGNOSTIC_CONTRACT.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_diagnostic_contract() -> dict:
    contract = json.loads(DIAGNOSTIC_CONTRACT.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 1
    assert contract["contract_id"] == "naqya-diagnostics-v1"
    assert contract["error_code_namespace"] == "NAQYA"
    assert contract["event_id_format"] == "NAQYA-EVT-<unix_ms>-<sequence>"
    assert contract["principles"]["offline_first"] is True
    assert contract["principles"]["no_sensitive_payloads"] is True

    actions = [item["id"] for item in contract["safe_actions"]]
    assert len(actions) == len(set(actions)) and actions
    codes = [item["code"] for item in contract["error_codes"]]
    assert len(codes) == len(set(codes)) and codes
    for code in codes:
        assert re.fullmatch(r"NAQYA-[A-Z]+-[0-9]{3}", code), f"Ungültiger Diagnosecode: {code}"
    action_set = set(actions)
    for item in contract["error_codes"]:
        assert item["safe_action"] in action_set, f"Unbekannte sichere Aktion für {item['code']}"
    return contract


def validate_schema_contract() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["title"] == "NAQYA Release Evidence"
    assert "desktop_package" in schema["required"]
    assert "whisper" in schema["required"]
    assert "diagnostics" in schema["required"]
    assert "validations" in schema["required"]


def main() -> None:
    validate_schema_contract()
    contract = validate_diagnostic_contract()
    if "--schema-only" in sys.argv:
        print("NAQYA Release-Nachweis-/Diagnose-Schema: PASS")
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
    assert target["os"] == "linux"
    assert target["architecture"] == "x86_64"
    assert target["rust_target"] == "x86_64-unknown-linux-gnu"

    for key in ("frontend", "whisper", "desktop_package"):
        item = evidence[key]
        hash_key = "manifest_sha256" if key == "frontend" else "sha256"
        assert re.fullmatch(r"[0-9a-f]{64}", item[hash_key]), f"Ungültiger SHA-256 in {key}"

    diagnostic = evidence["diagnostics"]
    assert diagnostic["contract_id"] == contract["contract_id"]
    assert diagnostic["contract_file"] == "diagnostics/DIAGNOSTIC_CONTRACT.json"
    assert diagnostic["contract_sha256"] == sha256_file(DIAGNOSTIC_CONTRACT)
    assert diagnostic["schema_version"] == contract["schema_version"]
    assert diagnostic["error_code_namespace"] == contract["error_code_namespace"]
    assert diagnostic["event_id_format"] == contract["event_id_format"]
    assert diagnostic["safe_action_ids"] == sorted(item["id"] for item in contract["safe_actions"])
    assert diagnostic["error_codes"] == sorted(item["code"] for item in contract["error_codes"])

    whisper = evidence["whisper"]
    assert whisper["provider"] == "ggml-org/whisper.cpp"
    assert whisper["tag"] == "v1.9.2"
    assert whisper["commit"] == "306c88f4d1286aec1bf96e544632897886af5501"
    assert whisper["build_profile"] == "cpu-release-static"
    assert whisper["bytes"] > 0
    assert evidence["desktop_package"]["bytes"] > 0

    validations = evidence["validations"]
    for key in (
        "frontend_manifest_verified",
        "diagnostic_contract_verified",
        "source_sidecar_sha_matches_packaged",
        "packaged_sidecar_started",
        "runtime_dependencies_resolved",
    ):
        assert validations[key] is True, f"Release-Gate nicht erfüllt: {key}"

    assert "2.11.4" in evidence["toolchain"]["tauri_cli"], "Tauri-CLI-Pin stimmt nicht"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        assert evidence["ci"]["provider"] == "github-actions"
        assert str(evidence["ci"]["run_id"] or "").isdigit()
        assert str(evidence["ci"]["run_number"] or "").isdigit()

    print("NAQYA Release-Nachweis inkl. Diagnosevertrag: PASS")


if __name__ == "__main__":
    main()
