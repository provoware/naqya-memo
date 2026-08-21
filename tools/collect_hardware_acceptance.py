#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "PROJEKTSTATUS.json"
DIAGNOSTICS_FILE = ROOT / "diagnostics/DIAGNOSTICS_CONTRACT.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_os() -> str:
    value = platform.system().lower()
    if value == "linux":
        return "linux"
    if value == "windows":
        return "windows"
    raise SystemExit(f"FEHLER: Nicht unterstütztes Betriebssystem: {platform.system()}")


def detect_architecture() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x86_64"
    raise SystemExit(f"FEHLER: Hardware-Abnahme ist derzeit nur für x86_64 definiert: {machine}")


def detect_cpu() -> str:
    cpu = platform.processor().strip()
    if cpu:
        return cpu
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
    return platform.machine() or "unbekannt"


def detect_ram_mb() -> int:
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/meminfo").read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("MemTotal:"):
                    return max(512, int(line.split()[1]) // 1024)
        except (OSError, ValueError, IndexError):
            pass
    if os.name == "nt":
        try:
            import ctypes

            class MemoryStatusEx(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatusEx()
            status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return max(512, int(status.ullTotalPhys // (1024 * 1024)))
        except (AttributeError, OSError):
            pass
    raise SystemExit("FEHLER: Gesamtspeicher konnte nicht zuverlässig ermittelt werden")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Erzeugt einen Hardware-Abnahmenachweis aus real gemessenen Werten."
    )
    parser.add_argument("--package", required=True, type=Path, help="Tatsächlich getestetes Installationspaket")
    parser.add_argument("--model", required=True, type=Path, help="Tatsächlich verwendete whisper.cpp-Modelldatei")
    parser.add_argument("--microphone", required=True, help="Bezeichnung des real getesteten Mikrofons")
    parser.add_argument("--profile", choices=("smoke", "long30", "long60"), required=True)
    parser.add_argument("--duration-seconds", type=int, required=True)
    parser.add_argument("--segments-total", type=int, required=True)
    parser.add_argument("--segments-lost", type=int, required=True)
    parser.add_argument("--realtime-factor-avg", type=float, required=True)
    parser.add_argument("--realtime-factor-max", type=float, required=True)
    parser.add_argument("--peak-ram-mb", type=float, required=True)
    parser.add_argument("--error-code", action="append", default=[], help="Beobachteter NAQYA-Diagnosecode; mehrfach erlaubt")
    parser.add_argument("--installed", action="store_true")
    parser.add_argument("--application-started", action="store_true")
    parser.add_argument("--bundled-sidecar-used", action="store_true")
    parser.add_argument("--protected-model-path-used", action="store_true")
    parser.add_argument("--microphone-capture-ok", action="store_true")
    parser.add_argument("--live-dictation-ok", action="store_true")
    parser.add_argument("--temp-wav-cleanup-ok", action="store_true")
    parser.add_argument("--result", choices=("PASS", "FAIL"), default="FAIL")
    parser.add_argument("--output", type=Path, default=Path("HARDWARE_ACCEPTANCE.json"))
    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> None:
    for label, path in (("Paket", args.package), ("Modell", args.model)):
        if not path.is_file():
            raise SystemExit(f"FEHLER: {label} fehlt oder ist keine Datei: {path}")
    if not args.microphone.strip():
        raise SystemExit("FEHLER: Mikrofonbezeichnung darf nicht leer sein")
    minimum = {"smoke": 1, "long30": 1800, "long60": 3600}[args.profile]
    if args.duration_seconds < minimum:
        raise SystemExit(f"FEHLER: Profil {args.profile} benötigt mindestens {minimum} Sekunden")
    if args.segments_total < 1 or not 0 <= args.segments_lost <= args.segments_total:
        raise SystemExit("FEHLER: Segmentwerte sind inkonsistent")
    if min(args.realtime_factor_avg, args.realtime_factor_max, args.peak_ram_mb) <= 0:
        raise SystemExit("FEHLER: RTF- und RAM-Messwerte müssen größer als 0 sein")

    if args.result == "PASS":
        confirmations = {
            "--installed": args.installed,
            "--application-started": args.application_started,
            "--bundled-sidecar-used": args.bundled_sidecar_used,
            "--protected-model-path-used": args.protected_model_path_used,
            "--microphone-capture-ok": args.microphone_capture_ok,
            "--live-dictation-ok": args.live_dictation_ok,
            "--temp-wav-cleanup-ok": args.temp_wav_cleanup_ok,
        }
        missing = [flag for flag, enabled in confirmations.items() if not enabled]
        if missing:
            raise SystemExit("FEHLER: PASS erfordert reale Bestätigung: " + ", ".join(missing))
        if args.segments_lost != 0:
            raise SystemExit("FEHLER: PASS ist bei Segmentverlust unzulässig")


def main() -> None:
    args = parse_args()
    validate_inputs(args)

    status = load_json(STATUS_FILE)
    diagnostics_contract = load_json(DIAGNOSTICS_FILE)
    expected_diag_sha = status["release_nachweis"]["diagnostics_contract"]["sha256"]
    actual_diag_sha = sha256_file(DIAGNOSTICS_FILE)
    if actual_diag_sha != expected_diag_sha:
        raise SystemExit("FEHLER: Diagnosevertrag stimmt nicht mit PROJEKTSTATUS.json überein")

    known_codes = set(diagnostics_contract["codes"])
    error_codes = sorted(set(args.error_code))
    unknown = [code for code in error_codes if code not in known_codes]
    if unknown:
        raise SystemExit("FEHLER: Unbekannte Diagnosecodes: " + ", ".join(unknown))

    record = {
        "schema_version": 1,
        "evidence_fingerprint": status["release_nachweis"]["evidence_fingerprint"],
        "test_profile": args.profile,
        "platform": {
            "os": detect_os(),
            "os_version": platform.version().strip() or platform.release().strip(),
            "architecture": detect_architecture(),
        },
        "device": {
            "cpu": detect_cpu(),
            "ram_mb": detect_ram_mb(),
            "microphone": args.microphone.strip(),
        },
        "package": {
            "file": str(args.package.resolve()),
            "sha256": sha256_file(args.package),
            "installed": args.installed,
            "application_started": args.application_started,
            "bundled_sidecar_used": args.bundled_sidecar_used,
        },
        "model": {
            "file": str(args.model.resolve()),
            "sha256": sha256_file(args.model),
            "protected_path_used": args.protected_model_path_used,
        },
        "audio": {
            "microphone_capture_ok": args.microphone_capture_ok,
            "live_dictation_ok": args.live_dictation_ok,
            "temp_wav_cleanup_ok": args.temp_wav_cleanup_ok,
            "provider": "whisper.cpp-sidecar",
        },
        "measurements": {
            "duration_seconds": args.duration_seconds,
            "segments_total": args.segments_total,
            "segments_lost": args.segments_lost,
            "realtime_factor_avg": args.realtime_factor_avg,
            "realtime_factor_max": args.realtime_factor_max,
            "peak_ram_mb": args.peak_ram_mb,
        },
        "diagnostics": {
            "contract_sha256": actual_diag_sha,
            "observed_error_codes": error_codes,
        },
        "result": args.result,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Hardware-Nachweis geschrieben: {args.output}")
    print(f"Ergebnis: {args.result} | Profil: {args.profile} | Segmente verloren: {args.segments_lost}")


if __name__ == "__main__":
    main()
