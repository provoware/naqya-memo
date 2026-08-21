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
RESOURCE_SCHEMA_VERSION = 1
RUNTIME_SCHEMA_VERSION = 1


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
                    ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatusEx()
            status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return max(512, int(status.ullTotalPhys // (1024 * 1024)))
        except (AttributeError, OSError):
            pass
    raise SystemExit("FEHLER: Gesamtspeicher konnte nicht zuverlässig ermittelt werden")


def load_resource_metrics(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"FEHLER: Ressourcenmessung fehlt oder ist keine Datei: {path}")
    try:
        record = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FEHLER: Ressourcenmessung ist kein gültiges JSON: {exc}") from exc
    required = {
        "schema_version", "duration_seconds", "sample_interval_ms", "peak_processes",
        "peak_ram_mb", "cpu_avg_pct", "cpu_max_pct", "command_exit_code",
    }
    missing = sorted(required - set(record))
    if missing:
        raise SystemExit("FEHLER: Ressourcenmessung unvollständig: " + ", ".join(missing))
    if record["schema_version"] != RESOURCE_SCHEMA_VERSION:
        raise SystemExit(f"FEHLER: Unbekannte Ressourcen-Schemaversion: {record['schema_version']}")
    if float(record["duration_seconds"]) <= 0 or float(record["peak_ram_mb"]) <= 0:
        raise SystemExit("FEHLER: Ressourcenmessung enthält keine positiven Laufzeit-/RAM-Werte")
    if int(record["sample_interval_ms"]) < 50 or int(record["peak_processes"]) < 1:
        raise SystemExit("FEHLER: Ressourcenmessung enthält ungültige Messparameter")
    if float(record["cpu_avg_pct"]) < 0 or float(record["cpu_max_pct"]) < float(record["cpu_avg_pct"]):
        raise SystemExit("FEHLER: Ressourcenmessung enthält inkonsistente CPU-Werte")
    if record["command_exit_code"] not in (None, 0):
        raise SystemExit("FEHLER: Ressourcenmessung stammt von einem fehlgeschlagenen Testprozess")
    return record


def load_runtime_metrics(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"FEHLER: Runtime-Messung fehlt oder ist keine Datei: {path}")
    try:
        record = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FEHLER: Runtime-Messung ist kein gültiges JSON: {exc}") from exc
    if record.get("format") == "NAQYA-LIVE-STT-RUNTIME":
        if record.get("schemaVersion") != RUNTIME_SCHEMA_VERSION or not isinstance(record.get("metrics"), dict):
            raise SystemExit("FEHLER: Runtime-Messung enthält einen ungültigen NAQYA-Envelope")
        metrics = record["metrics"]
    else:
        metrics = record
    required = {
        "schemaVersion", "targetSegmentMs", "segmentsTotal", "segmentsSucceeded", "segmentsLost",
        "capturedAudioMs", "transcribedAudioMs", "sttElapsedMs", "realtimeFactorAvg", "realtimeFactorMax",
    }
    missing = sorted(required - set(metrics))
    if missing:
        raise SystemExit("FEHLER: Runtime-Messung unvollständig: " + ", ".join(missing))
    if metrics["schemaVersion"] != RUNTIME_SCHEMA_VERSION:
        raise SystemExit(f"FEHLER: Unbekannte Runtime-Schemaversion: {metrics['schemaVersion']}")
    total = int(metrics["segmentsTotal"])
    succeeded = int(metrics["segmentsSucceeded"])
    lost = int(metrics["segmentsLost"])
    captured_ms = float(metrics["capturedAudioMs"])
    transcribed_ms = float(metrics["transcribedAudioMs"])
    elapsed_ms = float(metrics["sttElapsedMs"])
    rtf_avg = float(metrics["realtimeFactorAvg"])
    rtf_max = float(metrics["realtimeFactorMax"])
    if int(metrics["targetSegmentMs"]) <= 0 or total < 1 or succeeded < 0 or lost < 0 or succeeded + lost != total:
        raise SystemExit("FEHLER: Runtime-Messung enthält inkonsistente Segmentwerte")
    if captured_ms <= 0 or transcribed_ms <= 0 or transcribed_ms > captured_ms or elapsed_ms <= 0:
        raise SystemExit("FEHLER: Runtime-Messung enthält inkonsistente Audio-/STT-Zeiten")
    if rtf_avg <= 0 or rtf_max < rtf_avg:
        raise SystemExit("FEHLER: Runtime-Messung enthält inkonsistente RTF-Werte")
    calculated_avg = elapsed_ms / transcribed_ms
    if abs(calculated_avg - rtf_avg) > max(0.00001, calculated_avg * 0.00002):
        raise SystemExit("FEHLER: Runtime-Messung enthält einen nicht reproduzierbaren RTF-Durchschnitt")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Erzeugt einen Hardware-Abnahmenachweis aus real gemessenen Werten.")
    parser.add_argument("--package", required=True, type=Path, help="Tatsächlich getestetes Installationspaket")
    parser.add_argument("--model", required=True, type=Path, help="Tatsächlich verwendete whisper.cpp-Modelldatei")
    parser.add_argument("--microphone", required=True, help="Bezeichnung des real getesteten Mikrofons")
    parser.add_argument("--profile", choices=("smoke", "long30", "long60"), required=True)
    parser.add_argument("--runtime-metrics", type=Path, help="E3 nativeSttRuntimeMetrics als JSON; ersetzt manuelle Segment-/RTF-Werte")
    parser.add_argument("--duration-seconds", type=int)
    parser.add_argument("--segments-total", type=int)
    parser.add_argument("--segments-lost", type=int)
    parser.add_argument("--realtime-factor-avg", type=float)
    parser.add_argument("--realtime-factor-max", type=float)
    resources = parser.add_mutually_exclusive_group(required=True)
    resources.add_argument("--peak-ram-mb", type=float, help="Manuell übernommener Peak-RAM-Wert (Legacy/Fallback)")
    resources.add_argument("--resource-metrics", type=Path, help="RESOURCE_METRICS.json aus measure_process_resources.py")
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


def resolve_runtime_values(args: argparse.Namespace) -> tuple[dict | None, int, int, int, float, float]:
    manual_names = ("duration_seconds", "segments_total", "segments_lost", "realtime_factor_avg", "realtime_factor_max")
    if args.runtime_metrics:
        supplied = [name for name in manual_names if getattr(args, name) is not None]
        if supplied:
            raise SystemExit("FEHLER: --runtime-metrics darf nicht mit manuellen Segment-/RTF-Werten kombiniert werden")
        runtime = load_runtime_metrics(args.runtime_metrics)
        duration_seconds = int(float(runtime["capturedAudioMs"]) // 1000)
        return (
            runtime,
            duration_seconds,
            int(runtime["segmentsTotal"]),
            int(runtime["segmentsLost"]),
            float(runtime["realtimeFactorAvg"]),
            float(runtime["realtimeFactorMax"]),
        )
    missing = ["--" + name.replace("_", "-") for name in manual_names if getattr(args, name) is None]
    if missing:
        raise SystemExit("FEHLER: Ohne --runtime-metrics fehlen manuelle Messwerte: " + ", ".join(missing))
    return (
        None,
        int(args.duration_seconds),
        int(args.segments_total),
        int(args.segments_lost),
        float(args.realtime_factor_avg),
        float(args.realtime_factor_max),
    )


def validate_inputs(
    args: argparse.Namespace,
    peak_ram_mb: float,
    duration_seconds: int,
    segments_total: int,
    segments_lost: int,
    realtime_factor_avg: float,
    realtime_factor_max: float,
) -> None:
    for label, path in (("Paket", args.package), ("Modell", args.model)):
        if not path.is_file():
            raise SystemExit(f"FEHLER: {label} fehlt oder ist keine Datei: {path}")
    if not args.microphone.strip():
        raise SystemExit("FEHLER: Mikrofonbezeichnung darf nicht leer sein")
    minimum = {"smoke": 1, "long30": 1800, "long60": 3600}[args.profile]
    if duration_seconds < minimum:
        raise SystemExit(f"FEHLER: Profil {args.profile} benötigt mindestens {minimum} Sekunden")
    if segments_total < 1 or not 0 <= segments_lost <= segments_total:
        raise SystemExit("FEHLER: Segmentwerte sind inkonsistent")
    if min(realtime_factor_avg, realtime_factor_max, peak_ram_mb) <= 0:
        raise SystemExit("FEHLER: RTF- und RAM-Messwerte müssen größer als 0 sein")

    if args.result == "PASS":
        confirmations = {
            "--installed": args.installed, "--application-started": args.application_started,
            "--bundled-sidecar-used": args.bundled_sidecar_used,
            "--protected-model-path-used": args.protected_model_path_used,
            "--microphone-capture-ok": args.microphone_capture_ok,
            "--live-dictation-ok": args.live_dictation_ok,
            "--temp-wav-cleanup-ok": args.temp_wav_cleanup_ok,
        }
        missing = [flag for flag, enabled in confirmations.items() if not enabled]
        if missing:
            raise SystemExit("FEHLER: PASS erfordert reale Bestätigung: " + ", ".join(missing))
        if segments_lost != 0:
            raise SystemExit("FEHLER: PASS ist bei Segmentverlust unzulässig")


def main() -> None:
    args = parse_args()
    runtime_metrics, duration_seconds, segments_total, segments_lost, rtf_avg, rtf_max = resolve_runtime_values(args)
    resource_metrics = load_resource_metrics(args.resource_metrics) if args.resource_metrics else None
    peak_ram_mb = float(resource_metrics["peak_ram_mb"]) if resource_metrics else float(args.peak_ram_mb)
    validate_inputs(args, peak_ram_mb, duration_seconds, segments_total, segments_lost, rtf_avg, rtf_max)

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

    measurements = {
        "duration_seconds": duration_seconds,
        "segments_total": segments_total,
        "segments_lost": segments_lost,
        "realtime_factor_avg": rtf_avg,
        "realtime_factor_max": rtf_max,
        "peak_ram_mb": peak_ram_mb,
    }
    if runtime_metrics:
        measurements.update({
            "runtime_metrics_sha256": sha256_file(args.runtime_metrics),
            "segments_succeeded": int(runtime_metrics["segmentsSucceeded"]),
            "runtime_target_segment_ms": int(runtime_metrics["targetSegmentMs"]),
            "runtime_captured_audio_ms": float(runtime_metrics["capturedAudioMs"]),
            "runtime_transcribed_audio_ms": float(runtime_metrics["transcribedAudioMs"]),
            "runtime_stt_elapsed_ms": float(runtime_metrics["sttElapsedMs"]),
        })
    if resource_metrics:
        measurements.update({
            "resource_metrics_sha256": sha256_file(args.resource_metrics),
            "resource_duration_seconds": float(resource_metrics["duration_seconds"]),
            "cpu_avg_pct": float(resource_metrics["cpu_avg_pct"]),
            "cpu_max_pct": float(resource_metrics["cpu_max_pct"]),
        })

    record = {
        "schema_version": 1,
        "evidence_fingerprint": status["release_nachweis"]["evidence_fingerprint"],
        "test_profile": args.profile,
        "platform": {"os": detect_os(), "os_version": platform.version().strip() or platform.release().strip(), "architecture": detect_architecture()},
        "device": {"cpu": detect_cpu(), "ram_mb": detect_ram_mb(), "microphone": args.microphone.strip()},
        "package": {
            "file": str(args.package.resolve()), "sha256": sha256_file(args.package), "installed": args.installed,
            "application_started": args.application_started, "bundled_sidecar_used": args.bundled_sidecar_used,
        },
        "model": {"file": str(args.model.resolve()), "sha256": sha256_file(args.model), "protected_path_used": args.protected_model_path_used},
        "audio": {
            "microphone_capture_ok": args.microphone_capture_ok, "live_dictation_ok": args.live_dictation_ok,
            "temp_wav_cleanup_ok": args.temp_wav_cleanup_ok, "provider": "whisper.cpp-sidecar",
        },
        "measurements": measurements,
        "diagnostics": {"contract_sha256": actual_diag_sha, "observed_error_codes": error_codes},
        "result": args.result,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Hardware-Nachweis geschrieben: {args.output}")
    resource_source = "RESOURCE_METRICS.json" if resource_metrics else "manuell"
    runtime_source = "nativeSttRuntimeMetrics" if runtime_metrics else "manuell"
    print(f"Ergebnis: {args.result} | Profil: {args.profile} | Peak-RAM: {peak_ram_mb:.3f} MB ({resource_source}) | Runtime: {runtime_source} | Segmente verloren: {segments_lost}")


if __name__ == "__main__":
    main()
