from __future__ import annotations
from pathlib import Path
import sqlite3, hashlib, datetime, uuid

def migrate_v1_to_v2(db_path: Path, migration_sql_path: Path) -> dict:
    db_path=Path(db_path); sql=Path(migration_sql_path).read_text(encoding="utf-8")
    checksum=hashlib.sha256(sql.encode("utf-8")).hexdigest()
    conn=sqlite3.connect(db_path)
    try:
        version_row=conn.execute("SELECT value FROM meta WHERE key='database_schema_version'").fetchone()
        before=int(version_row[0]) if version_row else 1
        if before >= 2:
            return {"changed":False,"from":before,"to":before,"checksum":checksum}
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations(migration_id,from_version,to_version,applied_at,checksum_sha256,result) VALUES(?,?,?,?,?,?)",
            (str(uuid.uuid4()),1,2,datetime.datetime.now(datetime.timezone.utc).isoformat(),checksum,"SUCCESS"),
        )
        conn.commit()
        after=int(conn.execute("SELECT value FROM meta WHERE key='database_schema_version'").fetchone()[0])
        return {"changed":True,"from":before,"to":after,"checksum":checksum}
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()
