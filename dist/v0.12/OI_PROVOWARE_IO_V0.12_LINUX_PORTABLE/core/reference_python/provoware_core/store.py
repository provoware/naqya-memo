from __future__ import annotations
from pathlib import Path
import sqlite3, json, hashlib, datetime, uuid
from .contracts import OperationEvidence

def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def canonical_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def checksum_payload(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

class CoreStore:
    """Reference implementation of the V0.2 persistence contract.

    SQLite is canonical for structured records. Files such as audio/PDF remain
    external assets referenced by IDs and protected by their own manifests.
    """

    def __init__(self, db_path: Path, schema_path: Path):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.executescript(self.schema_path.read_text(encoding="utf-8"))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create_profile(self, display_name: str, pin_hash: str) -> str:
        if not display_name.strip():
            raise ValueError("PROFILE_NAME_EMPTY")
        if not pin_hash:
            raise ValueError("PIN_HASH_EMPTY")
        profile_id = str(uuid.uuid4())
        now = utc_now()
        with self.conn:
            self.conn.execute(
                """INSERT INTO profiles
                   (id, display_name, pin_hash, created_at, updated_at, revision, status)
                   VALUES (?, ?, ?, ?, ?, 1, 'ACTIVE')""",
                (profile_id, display_name.strip(), pin_hash, now, now),
            )
        return profile_id

    def upsert_entity(self, *, profile_id: str, entity_type: str, title: str,
                      payload: dict, entity_id: str | None = None,
                      expected_revision: int | None = None) -> tuple[str, int]:
        evidence = OperationEvidence.begin("UPSERT_ENTITY", [entity_id] if entity_id else [])
        if not entity_type:
            raise ValueError("ENTITY_TYPE_EMPTY")
        now = utc_now()
        entity_id = entity_id or str(uuid.uuid4())
        checksum = checksum_payload(payload)
        payload_json = canonical_json(payload)

        try:
            with self.conn:
                row = self.conn.execute(
                    "SELECT revision FROM entities WHERE id=?",
                    (entity_id,)
                ).fetchone()

                if row is None:
                    revision = 1
                    self.conn.execute(
                        """INSERT INTO entities
                        (id, profile_id, entity_type, schema_version, revision, status,
                         title, payload_json, checksum_sha256, created_at, updated_at)
                        VALUES (?, ?, ?, 1, ?, 'ACTIVE', ?, ?, ?, ?, ?)""",
                        (entity_id, profile_id, entity_type, revision, title,
                         payload_json, checksum, now, now),
                    )
                else:
                    current = int(row[0])
                    if expected_revision is not None and current != expected_revision:
                        raise RuntimeError("REVISION_CONFLICT")
                    revision = current + 1
                    self.conn.execute(
                        """UPDATE entities
                           SET title=?, payload_json=?, checksum_sha256=?,
                               revision=?, updated_at=?
                           WHERE id=?""",
                        (title, payload_json, checksum, revision, now, entity_id),
                    )

                self.conn.execute(
                    """INSERT INTO operation_journal
                    (operation_id, profile_id, operation_type, target_ids_json, state,
                     started_at, committed_at, pre_result_json, post_result_json,
                     rollback_result_json, error_code, evidence_json)
                    VALUES (?, ?, 'UPSERT_ENTITY', ?, 'COMMITTED', ?, ?, ?, ?, NULL, NULL, ?)""",
                    (
                        evidence.operation_id, profile_id, json.dumps([entity_id]),
                        now, utc_now(),
                        json.dumps({"profile_exists": True}),
                        json.dumps({"revision": revision, "checksum": checksum}),
                        json.dumps({"reference": "V0.2"}),
                    )
                )
            return entity_id, revision
        except Exception:
            # sqlite context manager rolls the transaction back.
            raise

    def get_entity(self, entity_id: str) -> dict | None:
        row = self.conn.execute(
            """SELECT id, profile_id, entity_type, schema_version, revision, status,
                      title, payload_json, checksum_sha256, created_at, updated_at, deleted_at
               FROM entities WHERE id=?""",
            (entity_id,)
        ).fetchone()
        if row is None:
            return None
        payload = json.loads(row[7])
        calculated = checksum_payload(payload)
        if calculated != row[8]:
            raise RuntimeError("CHECKSUM_MISMATCH")
        return {
            "id": row[0], "profile_id": row[1], "entity_type": row[2],
            "schema_version": row[3], "revision": row[4], "status": row[5],
            "title": row[6], "payload": payload, "checksum_sha256": row[8],
            "created_at": row[9], "updated_at": row[10], "deleted_at": row[11],
        }

    def soft_delete(self, entity_id: str, expected_revision: int | None = None) -> int:
        now = utc_now()
        with self.conn:
            row = self.conn.execute("SELECT revision FROM entities WHERE id=?", (entity_id,)).fetchone()
            if row is None:
                raise KeyError("ENTITY_NOT_FOUND")
            current = int(row[0])
            if expected_revision is not None and current != expected_revision:
                raise RuntimeError("REVISION_CONFLICT")
            revision = current + 1
            self.conn.execute(
                """UPDATE entities
                   SET status='TRASHED', deleted_at=?, updated_at=?, revision=?
                   WHERE id=?""",
                (now, now, revision, entity_id),
            )
        return revision



    def restore_entity(self, entity_id: str, expected_revision: int | None = None) -> int:
        now=utc_now()
        with self.conn:
            row=self.conn.execute("SELECT revision,status FROM entities WHERE id=?",(entity_id,)).fetchone()
            if row is None: raise KeyError("ENTITY_NOT_FOUND")
            current,status=int(row[0]),row[1]
            if expected_revision is not None and current!=expected_revision: raise RuntimeError("REVISION_CONFLICT")
            if status!="TRASHED": raise RuntimeError("ENTITY_NOT_TRASHED")
            revision=current+1
            self.conn.execute("UPDATE entities SET status='ACTIVE',deleted_at=NULL,updated_at=?,revision=? WHERE id=?",(now,revision,entity_id))
        return revision

    def record_undo(self, *, profile_id, operation_type, target_id, forward, inverse):
        entry_id=str(uuid.uuid4()); now=utc_now()
        with self.conn:
            self.conn.execute("INSERT INTO undo_journal(entry_id,profile_id,operation_type,target_id,forward_json,inverse_json,state,created_at) VALUES(?,?,?,?,?,?,'READY',?)",(entry_id,profile_id,operation_type,target_id,canonical_json(forward),canonical_json(inverse),now))
        return entry_id

    def undo_last(self, profile_id):
        row=self.conn.execute("SELECT entry_id,target_id,inverse_json FROM undo_journal WHERE profile_id=? AND state='READY' ORDER BY created_at DESC LIMIT 1",(profile_id,)).fetchone()
        if row is None: raise RuntimeError("UNDO_EMPTY")
        entry_id,target_id,data=row; inv=json.loads(data); target=self.get_entity(target_id)
        with self.conn:
            if "status" in inv:
                self.conn.execute("UPDATE entities SET status=?,deleted_at=CASE WHEN ?='ACTIVE' THEN NULL ELSE deleted_at END,revision=revision+1,updated_at=? WHERE id=?",(inv["status"],inv["status"],utc_now(),target_id))
            elif "payload" in inv:
                payload=inv["payload"]; title=inv.get("title",target["title"]); checksum=checksum_payload(payload)
                self.conn.execute("UPDATE entities SET title=?,payload_json=?,checksum_sha256=?,revision=revision+1,updated_at=? WHERE id=?",(title,canonical_json(payload),checksum,utc_now(),target_id))
            self.conn.execute("UPDATE undo_journal SET state='UNDONE',applied_at=? WHERE entry_id=?",(utc_now(),entry_id))
        return target_id

    def redo_last(self, profile_id):
        row=self.conn.execute("SELECT entry_id,target_id,forward_json FROM undo_journal WHERE profile_id=? AND state='UNDONE' ORDER BY applied_at DESC LIMIT 1",(profile_id,)).fetchone()
        if row is None: raise RuntimeError("REDO_EMPTY")
        entry_id,target_id,data=row; fwd=json.loads(data); target=self.get_entity(target_id)
        with self.conn:
            if "status" in fwd:
                self.conn.execute("UPDATE entities SET status=?,deleted_at=CASE WHEN ?='ACTIVE' THEN NULL ELSE COALESCE(deleted_at,?) END,revision=revision+1,updated_at=? WHERE id=?",(fwd["status"],fwd["status"],utc_now(),utc_now(),target_id))
            elif "payload" in fwd:
                payload=fwd["payload"]; title=fwd.get("title",target["title"]); checksum=checksum_payload(payload)
                self.conn.execute("UPDATE entities SET title=?,payload_json=?,checksum_sha256=?,revision=revision+1,updated_at=? WHERE id=?",(title,canonical_json(payload),checksum,utc_now(),target_id))
            self.conn.execute("UPDATE undo_journal SET state='READY',applied_at=? WHERE entry_id=?",(utc_now(),entry_id))
        return target_id

    def integrity_check(self) -> str:
        return self.conn.execute("PRAGMA integrity_check").fetchone()[0]
