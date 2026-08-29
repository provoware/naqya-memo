from __future__ import annotations
from pathlib import Path
import sqlite3, json, hashlib, shutil, os

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_backup_generation(generation_dir: Path) -> dict:
    generation_dir = Path(generation_dir)
    manifest_path = generation_dir / "manifest.json"
    db_path = generation_dir / "core.sqlite3"
    if not manifest_path.exists() or not db_path.exists():
        raise RuntimeError("BACKUP_GENERATION_INCOMPLETE")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = sha256_file(db_path)
    if actual != manifest.get("sha256"):
        raise RuntimeError("BACKUP_CHECKSUM_MISMATCH")
    conn = sqlite3.connect(db_path)
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        conn.close()
    if integrity != "ok":
        raise RuntimeError("BACKUP_SQLITE_INTEGRITY_FAILED")
    return manifest

def restore_backup_to_fresh_project(generation_dir: Path, fresh_project_dir: Path) -> Path:
    manifest = validate_backup_generation(generation_dir)
    fresh_project_dir = Path(fresh_project_dir)
    if fresh_project_dir.exists() and any(fresh_project_dir.iterdir()):
        raise RuntimeError("RESTORE_TARGET_NOT_EMPTY")
    data_dir = fresh_project_dir / "daten"
    data_dir.mkdir(parents=True, exist_ok=True)
    src = Path(generation_dir) / "core.sqlite3"
    dst = data_dir / "core.sqlite3"
    shutil.copy2(src, dst)

    # Verify copied restore, not the source snapshot.
    if sha256_file(dst) != manifest["sha256"]:
        dst.unlink(missing_ok=True)
        raise RuntimeError("RESTORE_COPY_HASH_MISMATCH")
    conn = sqlite3.connect(dst)
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        conn.close()
    if integrity != "ok":
        raise RuntimeError("RESTORE_SQLITE_INTEGRITY_FAILED")
    return dst
