from __future__ import annotations
import datetime, json, uuid

def parse_dt(value: str | None):
    if not value: return None
    return datetime.datetime.fromisoformat(value.replace("Z","+00:00"))

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class ReminderEngine:
    """Platform-neutral reminder acceptance engine.

    It does not claim OS delivery by itself. It decides what SHOULD be delivered
    and records deduplication evidence. Platform adapters perform actual delivery.
    """
    def __init__(self, store):
        self.store=store
        with self.store.conn:
            self.store.conn.execute("""CREATE TABLE IF NOT EXISTS reminder_delivery(
                delivery_id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                reminder_at TEXT NOT NULL,
                delivered_at TEXT NOT NULL,
                platform TEXT NOT NULL,
                result TEXT NOT NULL,
                UNIQUE(profile_id, entity_id, reminder_at, platform)
            )""")

    def due_items(self, profile_id: str, now: datetime.datetime | None = None):
        now=now or utc_now()
        rows=self.store.conn.execute(
            """SELECT id,entity_type,title,payload_json,revision
               FROM entities
               WHERE profile_id=? AND status='ACTIVE'
                 AND entity_type IN ('todo','calendar_event')""",(profile_id,)
        ).fetchall()
        out=[]
        for r in rows:
            payload=json.loads(r[3]); rem=parse_dt(payload.get("reminder_at"))
            if rem and rem <= now:
                out.append({"id":r[0],"entity_type":r[1],"title":r[2],"payload":payload,"revision":r[4]})
        out.sort(key=lambda x:x["payload"].get("reminder_at",""))
        return out

    def already_delivered(self, profile_id: str, entity_id: str, reminder_at: str, platform: str):
        return self.store.conn.execute(
            "SELECT 1 FROM reminder_delivery WHERE profile_id=? AND entity_id=? AND reminder_at=? AND platform=?",
            (profile_id,entity_id,reminder_at,platform)
        ).fetchone() is not None

    def mark_delivered(self, profile_id: str, entity_id: str, reminder_at: str, platform: str, result: str="DELIVERED"):
        did=str(uuid.uuid4())
        with self.store.conn:
            self.store.conn.execute(
                """INSERT OR IGNORE INTO reminder_delivery
                   (delivery_id,profile_id,entity_id,reminder_at,delivered_at,platform,result)
                   VALUES (?,?,?,?,?,?,?)""",
                (did,profile_id,entity_id,reminder_at,utc_now().isoformat(),platform,result)
            )
        return did

    def pending_for_platform(self, profile_id: str, platform: str, now: datetime.datetime | None = None):
        result=[]
        for x in self.due_items(profile_id,now):
            rem=x["payload"]["reminder_at"]
            if not self.already_delivered(profile_id,x["id"],rem,platform):
                result.append(x)
        return result
