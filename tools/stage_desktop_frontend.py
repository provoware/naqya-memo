#!/usr/bin/env python3
"""Stage the exact NAQYA web runtime for Tauri desktop bundles.

The staging directory is generated and never committed. Keeping an explicit
allowlist prevents repository documentation, tests, models, build caches or
other developer-only files from entering the desktop frontend payload.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"
MANIFEST_NAME = "NAQYA_FRONTEND_MANIFEST.json"
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source(relative: str) -> Path:
    source = ROOT / relative
    if not source.is_file():
        raise SystemExit(f"FEHLER: Runtime-Datei fehlt: {relative}")
    if source.is_symlink():
        raise SystemExit(f"FEHLER: Symlinks sind im Desktop-Frontend nicht erlaubt: {relative}")
    if source.resolve().parent != (ROOT / relative).resolve().parent:
        raise SystemExit(f"FEHLER: Runtime-Pfad ist nicht kanonisch: {relative}")
    return source


def main() -> None:
    sources = [(relative, validate_source(relative)) for relative in RUNTIME_FILES]
    if OUTPUT.exists():
        if OUTPUT.is_symlink():
            raise SystemExit("FEHLER: dist darf kein Symlink sein.")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    manifest_files = []
    for relative, source in sources:
        target = OUTPUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest_files.append(
            {
                "path": relative,
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
        )

    manifest = {
        "schema_version": 1,
        "purpose": "NAQYA deterministic Tauri frontend staging",
        "files": manifest_files,
    }
    (OUTPUT / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    staged = sorted(
        str(path.relative_to(OUTPUT))
        for path in OUTPUT.rglob("*")
        if path.is_file() and path.name != MANIFEST_NAME
    )
    expected = sorted(RUNTIME_FILES)
    if staged != expected:
        raise SystemExit(f"FEHLER: Staging-Abweichung. Soll={expected!r} Ist={staged!r}")

    print(f"NAQYA Desktop-Frontend: PASS ({len(expected)} Runtime-Dateien)")
    print(f"Ausgabe: {OUTPUT}")


if __name__ == "__main__":
    main()
