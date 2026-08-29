from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Literal

Traffic = Literal["GREEN","YELLOW","RED"]
PermissionState = Literal["GRANTED","DENIED","UNKNOWN","NOT_REQUIRED","USER_ACTION_REQUIRED"]

@dataclass
class CapabilityReport:
    platform_id: str
    os_name: str
    os_version: str
    architecture: str
    python_version: str
    display_width: int | None
    display_height: int | None
    capabilities: dict
    notes: list[str]

    def as_dict(self): return asdict(self)

@dataclass
class PermissionReport:
    platform_id: str
    permissions: dict[str, PermissionState]
    notes: list[str]

    def as_dict(self): return asdict(self)

class PlatformAdapter:
    platform_id = "unknown"
    def scan_capabilities(self) -> CapabilityReport: raise NotImplementedError
    def scan_permissions(self) -> PermissionReport: raise NotImplementedError
