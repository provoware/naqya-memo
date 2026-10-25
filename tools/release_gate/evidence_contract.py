"""Kanonische, fail-closed Auswertung bereits erzeugter Release-Evidence.

Dies prüft Struktur und Mindestbedingungen, NICHT die Echtheit physischer Tests.
Eine lokale JSON-Datei ist allein kein unabhängiger Geräte-Nachweis.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

GATES = (
    ("01", "8H_SOAK"),
    ("02", "CHROMIUM"),
    ("03", "FIREFOX"),
    ("04", "LINUX_MICROPHONE"),
    ("05", "STORAGE_FAILURE"),
    ("06", "ANDROID_DEVICE"),
    ("07", "IOS_IPHONE_X"),
)
STATUSES = frozenset(
    {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "PRECHECK_PASS", "RUNNING", "PRECHECK_RUNNING"}
)


def _invalid(gate: str, reason: str) -> dict:
    return {"gate": gate, "status": "INVALID_EVIDENCE", "reason": reason}


def read_gate(root: Path, number: str, name: str) -> dict:
    """Nur den exakten kanonischen Dateinamen und die passende Gate-ID werten."""
    gate = f"GATE_{number}_{name}"
    path = root / "registry" / "evidence" / "v0.12.2" / "gates" / f"{gate}.json"
    if path.is_symlink():
        return _invalid(gate, "SYMLINK_NOT_ALLOWED")
    if not path.exists():
        return {"gate": gate, "status": "NOT_RUN"}
    if not path.is_file():
        return _invalid(gate, "NOT_A_REGULAR_FILE")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return _invalid(gate, "UNREADABLE_OR_INVALID_JSON")
    if not isinstance(data, dict):
        return _invalid(gate, "NOT_A_JSON_OBJECT")
    if data.get("gate") != gate:
        return _invalid(gate, "GATE_ID_MISMATCH")
    if not isinstance(data.get("status"), str) or data["status"] not in STATUSES:
        return _invalid(gate, "UNKNOWN_STATUS")

    # Ein fünfsekündiger Preflight darf auch bei manipuliertem Status nie
    # als echter achtstündiger Dauertest gelten.
    if number == "01" and data["status"] == "PASS":
        required = data.get("required_seconds")
        executed = data.get("executed_seconds")
        valid_time = all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            and value >= 8 * 60 * 60
            and (not isinstance(value, float) or math.isfinite(value))
            for value in (required, executed)
        )
        if not (
            valid_time
            and data.get("qualification") == "FULL_8H"
            and data.get("integrity") == "ok"
            and data.get("errors") == []
        ):
            return _invalid(gate, "FULL_8H_EVIDENCE_REQUIRED")
    return data


def mobile_source_status(root: Path) -> str:
    path = root / "registry" / "evidence" / "v0.12.2" / "MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json"
    if path.is_symlink():
        return "INVALID_EVIDENCE"
    if not path.exists():
        return "NOT_RUN"
    if not path.is_file():
        return "INVALID_EVIDENCE"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return "INVALID_EVIDENCE"
    if not isinstance(data, dict) or not isinstance(data.get("status"), str):
        return "INVALID_EVIDENCE"
    return data["status"]
