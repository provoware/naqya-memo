from __future__ import annotations
import datetime
def require_title(title,code="TITLE_REQUIRED"):
    v=(title or "").strip()
    if not v: raise ValueError(code)
    if len(v)>240: raise ValueError("TITLE_TOO_LONG")
    return v
def ensure_iso_datetime(value,optional=True):
    if value in (None,""):
        if optional:return None
        raise ValueError("DATETIME_REQUIRED")
    try: datetime.datetime.fromisoformat(value.replace("Z","+00:00"))
    except Exception as e: raise ValueError("INVALID_DATETIME") from e
    return value
def utc_now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
