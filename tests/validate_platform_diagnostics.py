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
    "Diagnosevertrag driftet: Windows/Linux dürfen 0.5.1-C nicht still auseinanderlaufen. "
    f"Erwartet {EXPECTED_SHA256}, erhalten {actual_sha256}"
)

contract = json.loads(raw)
assert contract["schema_version"] == EXPECTED_SCHEMA
assert contract["event_schema_version"] == EXPECTED_EVENT_SCHEMA
assert contract["format"] == "NAQYA-DIAGNOSTICS"

# Der Code ist ein bewusst sichtbarer plattformübergreifender Semantikanker.
stt_4002 = contract["codes"]["NAQYA-STT-4002"]
assert stt_4002["category"] == "stt"
assert stt_4002["severity"] == "error"
assert stt_4002["what"] == "Live-STT-Segment konnte nicht transkribiert werden"
assert stt_4002["options"] == ["settings", "export-json", "export-text", "close"]

status = json.loads(STATUS.read_text(encoding="utf-8"))
evidence = status["release_nachweis"]
assert evidence["diagnostics_contract_sha256"] == EXPECTED_SHA256
assert evidence["diagnostics_schema_version"] == EXPECTED_SCHEMA
assert evidence["diagnostics_event_schema_version"] == EXPECTED_EVENT_SCHEMA

# 0.5.1-D darf den Plattformport erweitern, aber den Diagnosevertrag nicht verändern.
assert "WINDOWS-BUNDLE MIT IDENTISCHEM DIAGNOSEVERTRAG" in status["naechster_meilenstein"]

print("NAQYA Plattform-Diagnosevertrag: PASS")
