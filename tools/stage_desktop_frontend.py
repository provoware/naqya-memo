#!/usr/bin/env python3
"""Erzeugt das explizit freigegebene Desktop-Frontend ohne Buildsystem-Abhängigkeit."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SOURCE_DATE_EPOCH = int(os.environ.get("SOURCE_DATE_EPOCH", "946684800"))

# Kanonische Allowlist: Nur diese Dateien dürfen in die Tauri-Frontendquelle gelangen.
RUNTIME_FILES = (
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
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    missing = [rel for rel in RUNTIME_FILES if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit(f"FEHLER: Desktop-Runtime-Dateien fehlen: {', '.join(missing)}")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    manifest_files = []
    for rel in RUNTIME_FILES:
        source = ROOT / rel
        if source.is_symlink():
            raise SystemExit(f"FEHLER: Symlink ist im Desktop-Staging nicht erlaubt: {rel}")
        data = source.read_bytes()
        target = DIST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        os.utime(target, (SOURCE_DATE_EPOCH, SOURCE_DATE_EPOCH))
        manifest_files.append({"path": rel, "bytes": len(data), "sha256": sha256_bytes(data)})

    manifest = {
        "schema_version": 1,
        "purpose": "NAQYA deterministic desktop frontend staging",
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "files": manifest_files,
    }
    manifest_path = DIST / "BUILD_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.utime(manifest_path, (SOURCE_DATE_EPOCH, SOURCE_DATE_EPOCH))
    print(f"NAQYA Desktop-Staging: PASS ({len(RUNTIME_FILES)} Runtime-Dateien)")


if __name__ == "__main__":
    main()
