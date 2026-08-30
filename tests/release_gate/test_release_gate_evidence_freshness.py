from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "release_gate" / "evaluate_release_gate.py"
spec = importlib.util.spec_from_file_location("evaluate_release_gate", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

SHA_A = "a" * 40
SHA_B = "b" * 40


def test_current_run_evidence_passes():
    fresh, reason = module.evidence_freshness(
        {"timestamp": "2026-08-30T11:00:01+00:00"},
        "2026-08-30T11:00:00+00:00",
    )
    assert fresh is True
    assert reason == "CURRENT_GATE_RUN"


def test_equal_timestamp_is_not_rejected():
    fresh, reason = module.evidence_freshness(
        {"timestamp_utc": "2026-08-30T11:00:00Z"},
        "2026-08-30T11:00:00+00:00",
    )
    assert fresh is True
    assert reason == "CURRENT_GATE_RUN"


def test_old_pass_evidence_is_stale():
    fresh, reason = module.evidence_freshness(
        {"status": "PASS", "timestamp": "2026-08-30T10:59:59+00:00"},
        "2026-08-30T11:00:00+00:00",
    )
    assert fresh is False
    assert reason == "EVIDENCE_PREDATES_CURRENT_GATE_RUN"


def test_missing_run_context_fails_closed():
    fresh, reason = module.evidence_freshness(
        {"timestamp": "2026-08-30T11:00:01+00:00"},
        None,
    )
    assert fresh is False
    assert reason == "FRESHNESS_CONTEXT_MISSING_OR_INVALID"


def test_missing_evidence_timestamp_fails_closed():
    fresh, reason = module.evidence_freshness(
        {"status": "PASS"},
        "2026-08-30T11:00:00+00:00",
    )
    assert fresh is False
    assert reason == "EVIDENCE_TIMESTAMP_MISSING_OR_INVALID"


def test_naive_timestamp_fails_closed():
    fresh, reason = module.evidence_freshness(
        {"timestamp": "2026-08-30T11:00:01"},
        "2026-08-30T11:00:00+00:00",
    )
    assert fresh is False
    assert reason == "EVIDENCE_TIMESTAMP_MISSING_OR_INVALID"


def test_matching_source_identity_passes():
    valid, reason = module.source_identity(SHA_A, SHA_A)
    assert valid is True
    assert reason == "SOURCE_IDENTITY_MATCH"


def test_source_identity_change_fails_closed():
    valid, reason = module.source_identity(SHA_A, SHA_B)
    assert valid is False
    assert reason == "SOURCE_IDENTITY_CHANGED_DURING_GATE_RUN"


def test_missing_source_identity_context_fails_closed():
    valid, reason = module.source_identity(None, SHA_A)
    assert valid is False
    assert reason == "SOURCE_IDENTITY_CONTEXT_MISSING_OR_INVALID"


def test_invalid_current_source_identity_fails_closed():
    valid, reason = module.source_identity(SHA_A, "not-a-sha")
    assert valid is False
    assert reason == "CURRENT_SOURCE_IDENTITY_UNAVAILABLE"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"PASS total={len(tests)}")
