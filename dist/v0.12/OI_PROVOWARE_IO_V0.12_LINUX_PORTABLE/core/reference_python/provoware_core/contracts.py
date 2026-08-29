from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time, uuid

@dataclass
class ValidationResult:
    ok: bool
    code: str = "OK"
    details: dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationEvidence:
    operation_id: str
    operation_type: str
    started_monotonic: float
    target_ids: list[str]
    state: str = "PRE"
    pre: dict[str, Any] = field(default_factory=dict)
    post: dict[str, Any] = field(default_factory=dict)
    rollback: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def begin(cls, operation_type: str, target_ids: list[str] | None = None):
        return cls(
            operation_id=str(uuid.uuid4()),
            operation_type=operation_type,
            started_monotonic=time.monotonic(),
            target_ids=target_ids or [],
        )
