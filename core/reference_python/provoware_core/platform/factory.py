from __future__ import annotations
import sys
from .linux import LinuxAdapter
from .android import AndroidAdapter
from .ios import IOSAdapter

def get_platform_adapter(platform_id: str | None = None):
    pid=(platform_id or ("linux" if sys.platform.startswith("linux") else "ios" if sys.platform=="darwin" else "unknown")).lower()
    if pid == "linux": return LinuxAdapter()
    if pid == "android": return AndroidAdapter()
    if pid in ("ios","iphone"): return IOSAdapter()
    raise RuntimeError(f"PLATFORM_NOT_SUPPORTED:{pid}")
