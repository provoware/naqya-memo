from __future__ import annotations
from dataclasses import dataclass
import json
from .store import utc_now, canonical_json

THEMES = ("NEON_TUERKIS", "LILA_NACHT", "KNALLGELB_DUNKEL", "HOCHKONTRAST")
HELP_MODES = (1, 2, 3)
DEFAULTS = {
    "theme": "NEON_TUERKIS",
    "font_scale": 1.0,
    "help_mode": 2,
    "quote_rotation_enabled": True,
    "quote_rotation_minutes": 10,
    "developer_area_visible": False,
    "confirm_external_paths": True,
}

@dataclass
class SettingsService:
    store: object

    def ensure_defaults(self, profile_id: str) -> dict:
        for key, value in DEFAULTS.items():
            row = self.store.conn.execute(
                "SELECT 1 FROM profile_settings WHERE profile_id=? AND setting_key=?",
                (profile_id,key),
            ).fetchone()
            if row is None:
                self.set(profile_id,key,value)
        return self.get_all(profile_id)

    def _validate(self, key: str, value):
        if key == "theme" and value not in THEMES:
            raise ValueError("INVALID_THEME")
        if key == "font_scale" and not (0.8 <= float(value) <= 2.0):
            raise ValueError("FONT_SCALE_OUT_OF_RANGE")
        if key == "help_mode" and int(value) not in HELP_MODES:
            raise ValueError("INVALID_HELP_MODE")
        if key == "quote_rotation_minutes" and not (1 <= int(value) <= 1440):
            raise ValueError("INVALID_QUOTE_ROTATION")
        if key == "confirm_external_paths" and value is not True:
            raise ValueError("EXTERNAL_PATH_CONFIRMATION_CANNOT_BE_DISABLED_IN_V0_5")

    def set(self, profile_id: str, key: str, value):
        self._validate(key,value)
        now=utc_now(); encoded=canonical_json({"value":value})
        with self.store.conn:
            row=self.store.conn.execute(
                "SELECT revision FROM profile_settings WHERE profile_id=? AND setting_key=?",
                (profile_id,key),
            ).fetchone()
            if row is None:
                self.store.conn.execute(
                    "INSERT INTO profile_settings(profile_id,setting_key,value_json,revision,updated_at) VALUES(?,?,?,?,?)",
                    (profile_id,key,encoded,1,now),
                )
                return 1
            rev=int(row[0])+1
            self.store.conn.execute(
                "UPDATE profile_settings SET value_json=?,revision=?,updated_at=? WHERE profile_id=? AND setting_key=?",
                (encoded,rev,now,profile_id,key),
            )
            return rev

    def get(self, profile_id: str, key: str, default=None):
        row=self.store.conn.execute(
            "SELECT value_json FROM profile_settings WHERE profile_id=? AND setting_key=?",
            (profile_id,key),
        ).fetchone()
        return default if row is None else json.loads(row[0])["value"]

    def get_all(self, profile_id: str):
        rows=self.store.conn.execute(
            "SELECT setting_key,value_json FROM profile_settings WHERE profile_id=? ORDER BY setting_key",
            (profile_id,),
        ).fetchall()
        return {k:json.loads(v)["value"] for k,v in rows}
