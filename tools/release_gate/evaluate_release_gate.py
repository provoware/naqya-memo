"""Kanonische Release-Entscheidung: reale Gates bleiben ohne Belege NO-GO."""
from __future__ import annotations

import datetime
import json
from pathlib import Path

from evidence_contract import GATES, mobile_source_status, read_gate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json"
VERSION = ROOT / "registry/VERSION.json"

items = [read_gate(ROOT, number, name) for number, name in GATES]
pass_count = sum(item["status"] == "PASS" for item in items)
all_pass = pass_count == len(GATES)
source_status = mobile_source_status(ROOT)
source_pass = source_status == "PASS"
version = json.loads(VERSION.read_text(encoding="utf-8")).get("version", "UNKNOWN")
out = {
    "version": version,
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "feature_freeze": True,
    "freeze_exception": "platform parity completion only",
    "mobile_runtime_source_status": source_status,
    "required_real_gates": len(GATES),
    "passed_real_gates": pass_count,
    "all_required_real_gates_pass": all_pass,
    "release_status": "GO" if all_pass and source_pass else "NO-GO",
    "v1_rc_allowed": bool(all_pass and source_pass),
    "gates": items,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2, ensure_ascii=False))
raise SystemExit(0 if out["v1_rc_allowed"] else 2)
