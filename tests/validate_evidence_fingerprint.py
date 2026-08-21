#!/usr/bin/env python3
"""Billiger Vorabvertrag für den plattformneutralen Evidence-Fingerprint."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools/generate_release_evidence.py"
CONTRACT = ROOT / "diagnostics/DIAGNOSTICS_CONTRACT.json"
SCHEMA = ROOT / "release/RELEASE_EVIDENCE.schema.json"

spec = importlib.util.spec_from_file_location("naqya_release_evidence", GENERATOR)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
whisper = json.loads((ROOT / "src-tauri/sidecar/whisper-runtime.json").read_text(encoding="utf-8"))
diagnostics = json.loads(CONTRACT.read_text(encoding="utf-8"))
contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
source_commit = "1" * 40

fingerprint = module.evidence_fingerprint(version, source_commit, whisper, diagnostics, contract_sha)
assert set(fingerprint) == {"schema_version", "algorithm", "sha256", "diagnostic_codes_sha256", "inputs"}
assert fingerprint["schema_version"] == 1
assert fingerprint["algorithm"] == "sha256"
assert set(fingerprint["inputs"]) == {
    "fingerprint_schema_version",
    "naqya_version",
    "source_commit",
    "whisper_commit",
    "diagnostics_contract_sha256",
    "diagnostics_schema_version",
    "diagnostics_event_schema_version",
    "diagnostic_codes_sha256",
}

codes_raw = json.dumps(
    diagnostics["codes"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")
expected_codes_sha = hashlib.sha256(codes_raw).hexdigest()
assert fingerprint["diagnostic_codes_sha256"] == expected_codes_sha
assert fingerprint["inputs"]["diagnostic_codes_sha256"] == expected_codes_sha
assert fingerprint["sha256"] == hashlib.sha256(
    json.dumps(fingerprint["inputs"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()

# Paket, Zielplattform und Binärhashes dürfen den gemeinsamen Fingerprint nicht beeinflussen.
for forbidden in ("target", "target_os", "rust_target", "desktop_package", "package_sha256", "sidecar_sha256"):
    assert forbidden not in fingerprint["inputs"]

second = module.evidence_fingerprint(version, source_commit, whisper, diagnostics, contract_sha)
assert second == fingerprint, "Fingerprint ist bei identischen invarianten Eingaben nicht deterministisch"
changed = module.evidence_fingerprint(version, "2" * 40, whisper, diagnostics, contract_sha)
assert changed["sha256"] != fingerprint["sha256"], "Quellcommit muss den Fingerprint beeinflussen"

schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
assert "evidence_fingerprint" in schema["required"]
assert schema["properties"]["evidence_fingerprint"]["properties"]["algorithm"]["const"] == "sha256"
assert "evidence_fingerprint_verified" in schema["properties"]["validations"]["required"]

print(f"NAQYA Evidence-Fingerprint-Vertrag: PASS ({fingerprint['sha256']})")
