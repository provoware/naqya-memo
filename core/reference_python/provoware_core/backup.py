from __future__ import annotations
from pathlib import Path
import sqlite3, json, hashlib, datetime, shutil, uuid
from .atomic import atomic_write_bytes

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def create_verified_backup(db_path: Path, backup_root: Path) -> Path:
    """Create a consistent SQLite backup and a manifest, then restore-verify it."""
    db_path = Path(db_path)
    backup_root = Path(backup_root)
    backup_root.mkdir(parents=True, exist_ok=True)
    generation = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
    gen = backup_root / generation
    gen.mkdir(parents=True)

    backup_db = gen / "core.sqlite3"
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(backup_db)
    try:
        src.backup(dst)
        dst.commit()
    finally:
        dst.close()
        src.close()

    checksum = sha256_file(backup_db)
    verify = sqlite3.connect(backup_db)
    try:
        result = verify.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        verify.close()
    if result != "ok":
        shutil.rmtree(gen, ignore_errors=True)
        raise RuntimeError("BACKUP_RESTORE_VERIFY_FAILED")

    manifest = {
        "generation": generation,
        "database": "core.sqlite3",
        "sha256": checksum,
        "integrity_check": result,
        "verified_restore": True,
        "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    atomic_write_bytes(gen / "manifest.json", json.dumps(manifest, indent=2).encode("utf-8"))
    return gen
