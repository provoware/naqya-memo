#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "tools/collect_hardware_acceptance.py"
VALIDATOR = ROOT / "tests/validate_hardware_acceptance.py"
STATUS = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(COLLECTOR), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        package = temp / "naqya-test.pkg"
        model = temp / "ggml-test.bin"
        output = temp / "HARDWARE_ACCEPTANCE.json"
        resources = temp / "RESOURCE_METRICS.json"
        package_bytes = b"naqya-package-test\n"
        model_bytes = b"naqya-model-test\n"
        package.write_bytes(package_bytes)
        model.write_bytes(model_bytes)
        resource_record = {
            "schema_version": 1,
            "root_pid": 4242,
            "duration_seconds": 12.5,
            "sample_interval_ms": 250,
            "peak_processes": 2,
            "peak_ram_mb": 512.25,
            "cpu_avg_pct": 18.5,
            "cpu_max_pct": 41.75,
            "command_exit_code": 0,
        }
        resources.write_text(json.dumps(resource_record) + "\n", encoding="utf-8")

        base = (
            "--package", str(package),
            "--model", str(model),
            "--microphone", "NAQYA CI Test Microphone",
            "--profile", "smoke",
            "--duration-seconds", "12",
            "--segments-total", "4",
            "--segments-lost", "1",
            "--realtime-factor-avg", "0.42",
            "--realtime-factor-max", "0.61",
            "--resource-metrics", str(resources),
            "--output", str(output),
        )

        result = run(*base)
        assert result.returncode == 0, result.stdout
        record = json.loads(output.read_text(encoding="utf-8"))
        assert record["result"] == "FAIL"
        assert record["evidence_fingerprint"] == STATUS["release_nachweis"]["evidence_fingerprint"]
        assert record["package"]["sha256"] == sha256(package_bytes)
        assert record["model"]["sha256"] == sha256(model_bytes)
        assert record["measurements"]["segments_lost"] == 1
        assert record["measurements"]["peak_ram_mb"] == 512.25
        assert record["measurements"]["cpu_avg_pct"] == 18.5
        assert record["measurements"]["cpu_max_pct"] == 41.75
        assert record["measurements"]["resource_metrics_sha256"] == hashlib.sha256(resources.read_bytes()).hexdigest()
        assert record["package"]["installed"] is False
        assert record["audio"]["live_dictation_ok"] is False

        validated = subprocess.run(
            [sys.executable, str(VALIDATOR), str(output)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert validated.returncode == 0, validated.stdout

        unsafe_pass = run(*base, "--result", "PASS")
        assert unsafe_pass.returncode != 0
        assert "PASS erfordert reale Bestätigung" in unsafe_pass.stdout

        bad_resources = temp / "RESOURCE_METRICS_BAD.json"
        broken = dict(resource_record)
        broken["command_exit_code"] = 7
        bad_resources.write_text(json.dumps(broken) + "\n", encoding="utf-8")
        rejected = run(*base[:-4], "--resource-metrics", str(bad_resources), "--output", str(output))
        assert rejected.returncode != 0
        assert "fehlgeschlagenen Testprozess" in rejected.stdout

        legacy = run(
            "--package", str(package), "--model", str(model), "--microphone", "Legacy",
            "--profile", "smoke", "--duration-seconds", "2", "--segments-total", "1", "--segments-lost", "0",
            "--realtime-factor-avg", "1", "--realtime-factor-max", "1", "--peak-ram-mb", "384.5",
            "--output", str(output),
        )
        assert legacy.returncode == 0, legacy.stdout
        legacy_record = json.loads(output.read_text(encoding="utf-8"))
        assert legacy_record["measurements"]["peak_ram_mb"] == 384.5
        assert "resource_metrics_sha256" not in legacy_record["measurements"]

        long30_too_short = run(
            "--package", str(package), "--model", str(model), "--microphone", "Test",
            "--profile", "long30", "--duration-seconds", "1799", "--segments-total", "1", "--segments-lost", "0",
            "--realtime-factor-avg", "1", "--realtime-factor-max", "1", "--peak-ram-mb", "1",
            "--output", str(output),
        )
        assert long30_too_short.returncode != 0
        assert "mindestens 1800 Sekunden" in long30_too_short.stdout

    print("NAQYA Hardware-Collector Regression: PASS")


if __name__ == "__main__":
    main()
