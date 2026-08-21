#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "hardware/HARDWARE_ACCEPTANCE.schema.json"
STATUS = ROOT / "PROJEKTSTATUS.json"
DIAGNOSTICS = ROOT / "diagnostics/DIAGNOSTICS_CONTRACT.json"


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"FEHLER: Datei fehlt: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema_contract() -> None:
    schema = load_json(SCHEMA)
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["title"] == "NAQYA Hardware Acceptance"
    for key in ("evidence_fingerprint", "platform", "device", "package", "model", "audio", "measurements", "diagnostics", "result"):
        assert key in schema["required"], f"Schema-Pflichtfeld fehlt: {key}"
    assert schema["properties"]["result"]["enum"] == ["PASS", "FAIL"]
    measurement_properties = schema["properties"]["measurements"]["properties"]
    for key in ("resource_metrics_sha256", "resource_duration_seconds", "cpu_avg_pct", "cpu_max_pct"):
        assert key in measurement_properties, f"Ressourcen-Messfeld fehlt im Schema: {key}"


def require_sha(value: str, label: str) -> None:
    assert re.fullmatch(r"[0-9a-f]{64}", value), f"Ungültiger SHA-256: {label}"


def main() -> None:
    validate_schema_contract()
    if "--schema-only" in sys.argv:
        print("NAQYA Hardware-Abnahme-Schema: PASS")
        return
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: validate_hardware_acceptance.py <HARDWARE_ACCEPTANCE.json> | --schema-only")

    record = load_json(Path(sys.argv[1]))
    status = load_json(STATUS)
    diagnostics_contract = load_json(DIAGNOSTICS)

    assert record["schema_version"] == 1
    expected_fingerprint = status["release_nachweis"]["evidence_fingerprint"]
    assert record["evidence_fingerprint"] == expected_fingerprint, "Hardware-Nachweis gehört nicht zum aktuell validierten Softwarevertrag"
    require_sha(record["evidence_fingerprint"], "evidence_fingerprint")

    platform = record["platform"]
    assert platform["os"] in ("linux", "windows")
    assert platform["architecture"] == "x86_64"
    assert str(platform["os_version"]).strip()

    device = record["device"]
    assert str(device["cpu"]).strip()
    assert int(device["ram_mb"]) >= 512
    assert str(device["microphone"]).strip()

    package = record["package"]
    require_sha(package["sha256"], "package.sha256")
    assert str(package["file"]).strip()

    model = record["model"]
    require_sha(model["sha256"], "model.sha256")
    assert str(model["file"]).strip()

    audio = record["audio"]
    assert audio["provider"] == "whisper.cpp-sidecar"

    measurements = record["measurements"]
    assert measurements["duration_seconds"] >= 1
    assert measurements["segments_total"] >= 1
    assert 0 <= measurements["segments_lost"] <= measurements["segments_total"]
    assert measurements["realtime_factor_avg"] > 0
    assert measurements["realtime_factor_max"] > 0
    assert measurements["peak_ram_mb"] > 0

    resource_fields = ("resource_metrics_sha256", "resource_duration_seconds", "cpu_avg_pct", "cpu_max_pct")
    present_resource_fields = [key for key in resource_fields if key in measurements]
    assert len(present_resource_fields) in (0, len(resource_fields)), "Ressourcenherkunft muss vollständig oder gar nicht vorhanden sein"
    if present_resource_fields:
        require_sha(measurements["resource_metrics_sha256"], "measurements.resource_metrics_sha256")
        assert measurements["resource_duration_seconds"] > 0
        assert measurements["cpu_avg_pct"] >= 0
        assert measurements["cpu_max_pct"] >= measurements["cpu_avg_pct"]

    profile = record["test_profile"]
    minimum_duration = {"smoke": 1, "long30": 1800, "long60": 3600}[profile]
    assert measurements["duration_seconds"] >= minimum_duration, f"{profile}: Mindestdauer {minimum_duration}s unterschritten"

    diagnostics = record["diagnostics"]
    expected_contract_sha = status["release_nachweis"]["diagnostics_contract"]["sha256"]
    assert diagnostics["contract_sha256"] == expected_contract_sha
    assert diagnostics_contract["schema_version"] == 1
    for code in diagnostics["observed_error_codes"]:
        assert code in diagnostics_contract["codes"], f"Unbekannter Diagnosecode: {code}"

    if record["result"] == "PASS":
        for key in ("installed", "application_started", "bundled_sidecar_used"):
            assert package[key] is True, f"PASS unzulässig: package.{key} ist nicht bestätigt"
        assert model["protected_path_used"] is True, "PASS unzulässig: geschützter Modellpfad nicht bestätigt"
        for key in ("microphone_capture_ok", "live_dictation_ok", "temp_wav_cleanup_ok"):
            assert audio[key] is True, f"PASS unzulässig: audio.{key} ist nicht bestätigt"
        assert measurements["segments_lost"] == 0, "PASS unzulässig: Segmentverlust gemessen"

    print(f"NAQYA Hardware-Abnahme: PASS-VALIDIERT ({platform['os']}/{profile}, Ergebnis {record['result']})")


if __name__ == "__main__":
    main()
