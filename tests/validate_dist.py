#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

spec = importlib.util.spec_from_file_location("naqya_stage", ROOT / "tools/stage_desktop_frontend.py")
assert spec and spec.loader
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)

assert DIST.is_dir(), "dist/ fehlt – zuerst tools/stage_desktop_frontend.py ausführen"
manifest_path = DIST / "BUILD_MANIFEST.json"
assert manifest_path.is_file(), "dist/BUILD_MANIFEST.json fehlt"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
assert manifest["schema_version"] == 1

expected = set(stage.RUNTIME_FILES) | {"BUILD_MANIFEST.json"}
actual = {
    str(path.relative_to(DIST)).replace("\\", "/")
    for path in DIST.rglob("*")
    if path.is_file()
}
assert actual == expected, f"Desktop-Staging weicht von Allowlist ab: fehlt={sorted(expected-actual)}, extra={sorted(actual-expected)}"

rows = manifest["files"]
assert len(rows) == len(stage.RUNTIME_FILES)
assert len({row["path"] for row in rows}) == len(rows), "Doppelte Pfade im BUILD_MANIFEST"
for row in rows:
    rel = row["path"]
    assert rel in stage.RUNTIME_FILES, f"Nicht freigegebener Manifestpfad: {rel}"
    path = DIST / rel
    data = path.read_bytes()
    assert row["bytes"] == len(data), f"Größe stimmt nicht: {rel}"
    assert row["sha256"] == hashlib.sha256(data).hexdigest(), f"SHA-256 stimmt nicht: {rel}"

for forbidden in (".git", "tests", "docs", "src-tauri", ".sidecar-build", "node_modules"):
    assert not (DIST / forbidden).exists(), f"Verbotener Buildinhalt in dist/: {forbidden}"

print("NAQYA Desktop-Staging-Vertrag: PASS")
