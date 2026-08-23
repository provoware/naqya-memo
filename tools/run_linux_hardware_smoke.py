#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "tools/collect_hardware_acceptance.py"
VALIDATOR = ROOT / "tests/validate_hardware_acceptance.py"

CONFIRMATIONS = (
    ("installed", "Ist genau dieses Paket installiert?"),
    ("application-started", "Ist NAQYA auf diesem Gerät erfolgreich gestartet?"),
    ("bundled-sidecar-used", "Wurde der gebündelte naqya-whisper-Sidecar verwendet?"),
    ("protected-model-path-used", "Wurde das Modell aus dem geschützten NAQYA-Modellpfad verwendet?"),
    ("microphone-capture-ok", "Hat die Mikrofonaufnahme funktioniert?"),
    ("live-dictation-ok", "Hat das lokale Live-Diktat funktioniert?"),
    ("temp-wav-cleanup-ok", "Wurden temporäre WAV-Dateien nach dem Test bereinigt?"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Geführter, fail-closed E7-Linux-Hardware-Smoke für NAQYA."
    )
    parser.add_argument("--package", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--microphone")
    parser.add_argument("--runtime-metrics", type=Path)
    parser.add_argument("--resource-metrics", type=Path)
    parser.add_argument("--profile", choices=("smoke", "long30", "long60"), default="smoke")
    parser.add_argument("--output", type=Path, default=Path("HARDWARE_ACCEPTANCE.json"))
    parser.add_argument("--self-check", action="store_true", help="Nur Harness-Voraussetzungen prüfen")
    return parser.parse_args()


def require_linux() -> None:
    if not sys.platform.startswith("linux"):
        raise SystemExit("FEHLER: Dieser Assistent ist ausschließlich für Linux gedacht.")


def require_file(label: str, path: Path | None) -> None:
    if path is None:
        raise SystemExit(f"FEHLER: {label} wurde nicht angegeben.")
    if not path.is_file():
        raise SystemExit(f"FEHLER: {label} fehlt oder ist keine Datei: {path}")


def validate_harness() -> None:
    require_linux()
    require_file("Hardware-Collector", COLLECTOR)
    require_file("Hardware-Validator", VALIDATOR)


def validate_realtest_inputs(args: argparse.Namespace) -> None:
    validate_harness()
    require_file("Installationspaket", args.package)
    require_file("Whisper-Modell", args.model)
    require_file("Runtime-Metriken", args.runtime_metrics)
    require_file("Ressourcenmetriken", args.resource_metrics)
    if not (args.microphone or "").strip():
        raise SystemExit("FEHLER: Mikrofonbezeichnung wurde nicht angegeben.")


def ask_confirmation(question: str) -> bool:
    answer = input(f"{question} [ja/NEIN]: ").strip().lower()
    return answer == "ja"


def collect_confirmations() -> list[str]:
    print("\nE7 REALTEST – nur tatsächlich beobachtete Punkte mit 'ja' bestätigen.\n")
    flags = []
    for flag, question in CONFIRMATIONS:
        if ask_confirmation(question):
            flags.append(f"--{flag}")
    return flags


def build_collector_command(args: argparse.Namespace, flags: list[str]) -> list[str]:
    result = "PASS" if len(flags) == len(CONFIRMATIONS) else "FAIL"
    return [
        sys.executable,
        str(COLLECTOR),
        "--package", str(args.package),
        "--model", str(args.model),
        "--microphone", args.microphone,
        "--profile", args.profile,
        "--runtime-metrics", str(args.runtime_metrics),
        "--resource-metrics", str(args.resource_metrics),
        *flags,
        "--result", result,
        "--output", str(args.output),
    ]


def run_checked(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run_validation(output: Path) -> None:
    run_checked([sys.executable, str(VALIDATOR), str(output)])


def print_result(output: Path, passed: bool) -> None:
    print("\nErgebnis:")
    print(f"  Nachweis: {output}")
    print(f"  Status:   {'PASS' if passed else 'FAIL'}")
    if not passed:
        print("  Hinweis:  Keine Freigabe. Fehlende Punkte erneut real prüfen.")


def main() -> int:
    args = parse_args()
    if args.self_check:
        validate_harness()
        print("E7 Linux hardware smoke harness: SELF-CHECK OK")
        return 0
    validate_realtest_inputs(args)
    if not sys.stdin.isatty():
        raise SystemExit("FEHLER: Reale Bestätigungen benötigen ein interaktives Terminal.")
    flags = collect_confirmations()
    passed = len(flags) == len(CONFIRMATIONS)
    run_checked(build_collector_command(args, flags))
    run_validation(args.output)
    print_result(args.output, passed)
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
