from __future__ import annotations
from dataclasses import dataclass
import uuid
from .pin import hash_pin, verify_pin
from .store import utc_now

@dataclass
class ProfileService:
    store: object

    def create(self, display_name: str, pin: str) -> str:
        return self.store.create_profile(display_name, hash_pin(pin))

    def verify_access(self, profile_id: str, pin: str, source: str = "LOCAL") -> bool:
        row = self.store.conn.execute("SELECT pin_hash FROM profiles WHERE id=? AND status='ACTIVE'", (profile_id,)).fetchone()
        if row is None:
            raise KeyError("PROFILE_NOT_FOUND")
        ok = verify_pin(pin, row[0])
        with self.store.conn:
            self.store.conn.execute(
                "INSERT INTO profile_access_log(access_id,profile_id,attempted_at,result,source) VALUES(?,?,?,?,?)",
                (str(uuid.uuid4()), profile_id, utc_now(), "SUCCESS" if ok else "FAIL", source),
            )
        return ok

    def change_pin(self, profile_id: str, current_pin: str, new_pin: str) -> None:
        if not self.verify_access(profile_id, current_pin, source="PIN_CHANGE"):
            raise PermissionError("CURRENT_PIN_INVALID")
        encoded = hash_pin(new_pin)
        with self.store.conn:
            self.store.conn.execute(
                "UPDATE profiles SET pin_hash=?, revision=revision+1, updated_at=? WHERE id=?",
                (encoded, utc_now(), profile_id),
            )

    def access_history(self, profile_id: str, limit: int = 20):
        rows = self.store.conn.execute(
            "SELECT attempted_at,result,source FROM profile_access_log WHERE profile_id=? ORDER BY attempted_at DESC LIMIT ?",
            (profile_id, limit),
        ).fetchall()
        return [{"attempted_at":r[0],"result":r[1],"source":r[2]} for r in rows]
