from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = DIST / "NAQYA_FRONTEND_MANIFEST.json"
EXPECTED = {
    "index.html",
    "styles.css",
    "styles-02.css",
    "app.js",
    "sw.js",
    "manifest.webmanifest",
    "icons/icon.svg",
    "icons/icon-maskable.svg",
    "services/capabilities.js",
    "services/native-bridge.js",
    "services/stt-core.js",
    "services/audio-normalizer.js",
    "services/live-stt.js",
    "services/release-04.js",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


subprocess.run(["python3", "tools/stage_desktop_frontend.py"], cwd=ROOT, check=True)
assert DIST.is_dir() and not DIST.is_symlink(), "dist fehlt oder ist ein Symlink"
assert MANIFEST.is_file(), "Frontend-Manifest fehlt"

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
assert manifest["schema_version"] == 1
entries = manifest["files"]
paths = {entry["path"] for entry in entries}
assert paths == EXPECTED, f"Staging-Dateisatz weicht ab: {sorted(paths ^ EXPECTED)}"

actual = {
    str(path.relative_to(DIST))
    for path in DIST.rglob("*")
    if path.is_file() and path.name != MANIFEST.name
}
assert actual == EXPECTED, f"Unerwartete Dateien in dist: {sorted(actual ^ EXPECTED)}"

for entry in entries:
    target = DIST / entry["path"]
    source = ROOT / entry["path"]
    assert target.is_file() and source.is_file()
    assert not target.is_symlink()
    assert entry["bytes"] == target.stat().st_size == source.stat().st_size
    assert entry["sha256"] == sha256(target) == sha256(source)

config = json.loads((ROOT / "src-tauri/tauri.conf.json").read_text(encoding="utf-8"))
build = config["build"]
assert build["frontendDist"] == "../dist"
assert build["beforeBuildCommand"] == "python3 tools/stage_desktop_frontend.py"

index = (DIST / "index.html").read_text(encoding="utf-8")
for path in [
    "styles.css",
    "styles-02.css",
    "app.js",
    "services/capabilities.js",
    "services/native-bridge.js",
    "services/stt-core.js",
    "services/audio-normalizer.js",
    "services/live-stt.js",
    "services/release-04.js",
]:
    assert path in index, f"index.html referenziert Runtime-Datei nicht: {path}"

print("NAQYA Desktop-Frontend-Staging: PASS")
