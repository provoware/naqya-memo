from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "diagnostics" / "DIAGNOSTICS_CONTRACT.json"
STATUS = ROOT / "PROJEKTSTATUS.json"
EXPECTED_SHA256 = "fa160ea4cb259406ecd057ebfb225d862b4484f10dba4e83948755c6fda65425"
EXPECTED_SCHEMA = 1
EXPECTED_EVENT_SCHEMA = 1

raw = CONTRACT.read_bytes()
actual_sha256 = hashlib.sha256(raw).hexdigest()
assert actual_sha256 == EXPECTED_SHA256, (
    "Diagnosevertrag driftet: Linux und Windows müssen in 0.5.1-D bytegenau denselben Vertrag verwenden. "
    f"Erwartet {EXPECTED_SHA256}, erhalten {actual_sha256}"
)

contract = json.loads(raw)
assert contract["format"] == "NAQYA-DIAGNOSTICS"
assert contract["schema_version"] == EXPECTED_SCHEMA
assert contract["event_schema_version"] == EXPECTED_EVENT_SCHEMA

# Expliziter Semantikanker: derselbe Fehlercode muss auf jeder Plattform dasselbe bedeuten.
stt_4002 = contract["codes"]["NAQYA-STT-4002"]
assert stt_4002["category"] == "stt"
assert stt_4002["severity"] == "error"
assert stt_4002["what"] == "Live-STT-Segment konnte nicht transkribiert werden"
assert stt_4002["options"] == ["settings", "export-json", "export-text", "close"]

status = json.loads(STATUS.read_text(encoding="utf-8"))
evidence_contract = status["release_nachweis"]["diagnostics_contract"]
assert evidence_contract["file"] == "diagnostics/DIAGNOSTICS_CONTRACT.json"
assert evidence_contract["sha256"] == EXPECTED_SHA256
assert evidence_contract["schema_version"] == EXPECTED_SCHEMA
assert evidence_contract["event_schema_version"] == EXPECTED_EVENT_SCHEMA
assert evidence_contract["format"] == "NAQYA-DIAGNOSTICS"
assert status["naechster_meilenstein"].startswith("0.5.1-D – WINDOWS-X86_64-BUNDLE")

print("NAQYA Plattform-Diagnosevertrag: PASS")
