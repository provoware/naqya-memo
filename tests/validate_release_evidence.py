#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "release/RELEASE_EVIDENCE.schema.json"


def validate_schema_contract() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["title"] == "NAQYA Release Evidence"
    assert "desktop_package" in schema["required"]
    assert "whisper" in schema["required"]
    assert "validations" in schema["required"]


def main() -> None:
    validate_schema_contract()
    if "--schema-only" in sys.argv:
        print("NAQYA Release-Nachweis-Schema: PASS")
        return

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "release/RELEASE_EVIDENCE.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    assert evidence["schema_version"] == 1
    assert evidence["status"] == "bundle-validated"
    datetime.fromisoformat(evidence["generated_at"].replace("Z", "+00:00"))

    source = evidence["source"]
    assert source["repository"] == "provoware/naqya-memo"
    assert source["naqya_version"] == "0.5.0"
    assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])

    target = evidence["target"]
    assert target["os"] == "linux"
    assert target["architecture"] == "x86_64"
    assert target["rust_target"] == "x86_64-unknown-linux-gnu"

    for key in ("frontend", "whisper", "desktop_package"):
        item = evidence[key]
        hash_key = "manifest_sha256" if key == "frontend" else "sha256"
        assert re.fullmatch(r"[0-9a-f]{64}", item[hash_key]), f"Ungültiger SHA-256 in {key}"

    whisper = evidence["whisper"]
    assert whisper["provider"] == "ggml-org/whisper.cpp"
    assert whisper["tag"] == "v1.9.2"
    assert whisper["commit"] == "306c88f4d1286aec1bf96e544632897886af5501"
    assert whisper["build_profile"] == "cpu-release-static"
    assert whisper["bytes"] > 0

    package = evidence["desktop_package"]
    assert package["bytes"] > 0
    assert package["reproducibility_profile"] == "dpkg-deb-normalized-v1"
    assert package["source_date_epoch"] == 946684800

    validations = evidence["validations"]
    for key in (
        "frontend_manifest_verified",
        "source_sidecar_sha_matches_packaged",
        "packaged_sidecar_started",
        "runtime_dependencies_resolved",
        "package_repack_deterministic",
    ):
        assert validations[key] is True, f"Release-Gate nicht erfüllt: {key}"

    assert "2.11.4" in evidence["toolchain"]["tauri_cli"], "Tauri-CLI-Pin stimmt nicht"
    assert "dpkg-deb" in evidence["toolchain"]["dpkg_deb"], "dpkg-deb-Version fehlt"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        assert evidence["ci"]["provider"] == "github-actions"
        assert str(evidence["ci"]["run_id"] or "").isdigit()
        assert str(evidence["ci"]["run_number"] or "").isdigit()

    print("NAQYA Release-Nachweis inklusive DEB-Reproduzierbarkeit: PASS")


if __name__ == "__main__":
    main()
