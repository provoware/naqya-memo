#!/usr/bin/env python3
"""Read-only prerequisites for six NAQYA release gates; never executes gate scripts.

FOUND is not a PASS, a device acceptance, or even proof of browser execution.
Only the gate programs and canonical evaluator may change release evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATES = ("01", "02", "03", "04", "06", "07")
LABELS = {
    "01": "8H_SOAK",
    "02": "CHROMIUM",
    "03": "FIREFOX",
    "04": "LINUX_MICROPHONE",
    "06": "ANDROID_DEVICE",
    "07": "IOS_IPHONE_X",
}
COMMANDS = {
    "01": "./RUN_8H_SOAK_ONLY.sh",
    "02": "python3 -S tools/release_gate/gate_02_chromium.py",
    "03": "python3 -S tools/release_gate/gate_03_firefox.py",
    "04": "python3 -S tools/release_gate/gate_04_linux_microphone.py",
    "06": "python3 -S tools/release_gate/gate_06_android_device.py",
    "07": "python3 -S tools/release_gate/gate_07_ios_iphone_x.py",
}

def _playwright_node_available() -> bool:
    node = shutil.which("node")
    if not node:
        return False
    try:
        result = subprocess.run(
            [node, "-e", "require.resolve(process.env.PROVOWARE_PLAYWRIGHT_MODULE || 'playwright')"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0

def _exists_env(name: str, directory: bool = False) -> bool:
    value = os.environ.get(name, "").strip()
    if not value:
        return False
    p = Path(value).expanduser()
    return p.is_dir() if directory else p.is_file()

def inspect(number: str) -> dict:
    if number not in LABELS:
        raise ValueError("Unknown gate: " + number)
    missing = []
    def need(condition: bool, message: str) -> None:
        if not condition:
            missing.append(message)
    if number == "01":
        need((ROOT / "core/reference_python/provoware_core").is_dir(), "Python-Kern fehlt")
        need((ROOT / "schemas/core_schema_v2.sql").is_file(), "SQLite-Schema fehlt")
        need(shutil.which("python3") is not None, "Python 3 fehlt")
    elif number in ("02", "03"):
        executable = ("chromium", "chromium-browser") if number == "02" else ("firefox",)
        need(any(shutil.which(item) for item in executable), "Systembrowser fehlt")
        need(_playwright_node_available(), "Node-Playwright für echten Bedienungs-/Layouttest fehlt")
        need((ROOT / "tests/ui_consistency/runtime_safety_browser.cjs").is_file(),
             "Realer Browser-Bedienungstest fehlt")
        # Existing screenshot/version prechecks are insufficient for E2E release PASS.
    elif number == "04":
        need(shutil.which("ffmpeg") is not None, "FFmpeg fehlt")
        runtime = Path(os.environ.get("XDG_RUNTIME_DIR") or "/nonexistent")
        audio = (
            Path("/dev/snd").exists()
            or bool(os.environ.get("PULSE_SERVER"))
            or (runtime / "pulse/native").exists()
        )
        need(audio, "Kein ALSA-/Pulse-Audiozugang erkennbar")
    elif number == "06":
        need(shutil.which("adb") is not None, "ADB fehlt")
        need(_exists_env("PROVOWARE_ANDROID_ACCEPTANCE_APK") or _exists_env("PROVOWARE_ANDROID_APK"),
             "Debug-/Acceptance-APK fehlt")
        need(_exists_env("PROVOWARE_ANDROID_RELEASE_APK"), "Signierte Release-APK fehlt")
    elif number == "07":
        need(platform.system() == "Darwin", "macOS erforderlich")
        need(shutil.which("xcrun") is not None, "Xcode xcrun fehlt")
        need(shutil.which("xcodebuild") is not None, "Xcode build fehlt")
        need(_exists_env("PROVOWARE_IOS_APP", directory=True), "Signiertes .app-Bundle fehlt")
        need(bool(os.environ.get("PROVOWARE_IOS_DEVICE_ID", "").strip()), "iPhone-X-Geräte-ID fehlt")
    return {
        "gate": "GATE_" + number + "_" + LABELS[number],
        "prerequisites": "FOUND" if not missing else "BLOCKED",
        "missing": missing,
        "run_command": COMMANDS[number],
        "real_evidence": "NOT_CHECKED",
        "user_final_acceptance": "NOT_PERFORMED",
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Nur lesen; keine Geräte-, Daten- oder Evidence-Mutation.")
    parser.add_argument("--gate", choices=GATES)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    results = [inspect(n) for n in (args.gate,) if n] if args.gate else [inspect(n) for n in GATES]
    if args.json:
        print(json.dumps({"kind": "READ_ONLY_PREFLIGHT", "gates": results}, indent=2, ensure_ascii=False))
    else:
        for item in results:
            detail = "; ".join(item["missing"]) or "Voraussetzungen gefunden, REALTEST AUSSTEHEND"
            print(f'{item["gate"]}: {item["prerequisites"]} – {detail}')
            print(f'  Reale Prüfung getrennt starten: {item["run_command"]}')
    # Exit 2 means some prerequisites absent. Even exit 0 is NOT a release PASS.
    return 2 if any(item["prerequisites"] == "BLOCKED" for item in results) else 0

if __name__ == "__main__":
    sys.exit(main())
