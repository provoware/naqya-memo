"""Kanonische, fail-closed Auswertung bereits erzeugter Release-Evidence.

Dies prüft Struktur und Mindestbedingungen, NICHT die Echtheit physischer Tests.
Eine lokale JSON-Datei ist allein kein unabhängiger Geräte-Nachweis.
"""
from __future__ import annotations

import errno
import json
import math
import re
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


def _has_symlink_component(root: Path, path: Path) -> bool:
    """Keine Gate-Evidence durch symbolische Links in Elternverzeichnissen lesen."""
    current = root
    if current.is_symlink():
        return True
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False



def _invalid(gate: str, reason: str) -> dict:
    return {"gate": gate, "status": "INVALID_EVIDENCE", "reason": reason}


def read_gate(root: Path, number: str, name: str) -> dict:
    """Nur den exakten kanonischen Dateinamen und die passende Gate-ID werten."""
    gate = f"GATE_{number}_{name}"
    path = root / "registry" / "evidence" / "v0.12.2" / "gates" / f"{gate}.json"
    if _has_symlink_component(root, path):
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
    # Ein PASS ohne überprüfbare Aufnahmemetadaten darf keine reale
    # Mikrofonabnahme vortäuschen; dies beweist nicht die Hardware-Herkunft.
    if number == "04" and data["status"] == "PASS":
        seconds = data.get("physical_capture_seconds")
        size = data.get("bytes")
        digest = data.get("sha256")
        if not (
            isinstance(seconds, (int, float)) and not isinstance(seconds, bool)
            and seconds >= 2 and (not isinstance(seconds, float) or math.isfinite(seconds))
            and isinstance(size, int) and not isinstance(size, bool) and size > 0
            and isinstance(data.get("asset_id"), str) and bool(data["asset_id"].strip())
            and isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest)
        ):
            return _invalid(gate, "PHYSICAL_CAPTURE_EVIDENCE_REQUIRED")
    # A bare PASS flag cannot stand in for the two Linux kernel probes and
    # the application recovery matrix. This is structural validation only;
    # it does not authenticate the physical origin of the evidence file.
    if number == "05" and data["status"] == "PASS":
        probes = data.get("tests")
        if not isinstance(probes, dict) or set(probes) != {"dev_full", "read_only_mount"}:
            return _invalid(gate, "STORAGE_PROBES_REQUIRED")
        full = probes["dev_full"]
        readonly = probes["read_only_mount"]
        if not (
            isinstance(full, dict)
            and isinstance(readonly, dict)
            and full.get("status") == "PASS"
            and type(full.get("errno")) is int
            and full["errno"] == errno.ENOSPC
            and readonly.get("status") == "PASS"
            and type(readonly.get("errno")) is int
            and readonly["errno"] in (errno.EROFS, errno.EACCES, errno.EPERM)
            and data.get("application_failure_matrix_evidence_present") is True
            and data.get("application_failure_matrix_pass") is True
        ):
            return _invalid(gate, "STORAGE_RECOVERY_EVIDENCE_REQUIRED")
    # Ein Quellcode-Build oder unvollstaendiger JSON-PASS ist kein reales Android-Gate.
    # Nur Ergebnisfelder des physischen Debug-/Release-Ablaufs akzeptieren.
    if number == "06" and data["status"] == "PASS":
        required_text = (
            "adb", "acceptance_apk", "release_apk", "serial",
            "model", "sdk", "release_pid",
        )
        valid_device = (
            data.get("package") == "de.provoware.naqya"
            and data.get("runtime_source") == "V0.12.2"
            and all(
                isinstance(data.get(field), str) and bool(data[field].strip())
                for field in required_text
            )
            and isinstance(data.get("devices"), list)
            and data["devices"] == [data["serial"]]
            and data.get("reminder_fired") is True
            and data.get("release_version_name") == "0.12.2"
            and all(
                isinstance(data.get(field), dict)
                and data[field].get("mode") == mode
                and data[field].get("status") == "PASS"
                for field, mode in (
                    ("run_result", "run"), ("verify_result", "verify")
                )
            )
        )
        if not valid_device:
            return _invalid(gate, "ANDROID_DEVICE_EVIDENCE_REQUIRED")
    return data


def mobile_source_status(root: Path) -> str:
    path = root / "registry" / "evidence" / "v0.12.2" / "MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json"
    if _has_symlink_component(root, path):
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
