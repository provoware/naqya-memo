from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "app" / "server.py"

FALLBACK_MARKERS = (
    "SELECT id,display_name FROM profiles WHERE status='ACTIVE' ORDER BY created_at LIMIT 1",
    "profile_service.create('Standardprofil', '0000')",
)

REQUIRED_GUARD_MARKERS = (
    "PROFILE_CONTEXT_REQUIRED",
    "_require_profile_context",
)


def _has_implicit_profile_fallback(source: str) -> bool:
    return any(marker in source for marker in FALLBACK_MARKERS)


def _has_explicit_profile_api_boundary(source: str) -> bool:
    """Recognize the minimum source contract required before real Blanco runtime.

    The later runtime slice may refine route ownership, but it must first provide
    one named fail-closed profile guard and a stable error code. Requiring these
    markers makes removal of the historical fallback an explicit, reviewable
    transition instead of an accidental half-migration.
    """
    return all(marker in source for marker in REQUIRED_GUARD_MARKERS)


def _unsafe_blanco_transition(source: str) -> bool:
    return not _has_implicit_profile_fallback(source) and not _has_explicit_profile_api_boundary(source)


def test_real_blanco_requires_explicit_profile_api_boundary() -> None:
    source = SERVER.read_text(encoding="utf-8")
    assert not _unsafe_blanco_transition(source), (
        "BLANCO_PROFILE_API_BOUNDARY_MISSING: app/server.py hat den historischen "
        "Profilfallback entfernt, besitzt aber noch keinen zentralen fail-closed "
        "Profilkontext-Guard. Vor echtem Blanco müssen profilgebundene API-/Asset-"
        "Zugriffe über _require_profile_context mit PROFILE_CONTEXT_REQUIRED "
        "gesperrt werden."
    )


def test_detector_rejects_unguarded_synthetic_blanco() -> None:
    synthetic = "PROFILE_ID = None\nclass Handler:\n    def do_GET(self):\n        return api_state()\n"
    assert _unsafe_blanco_transition(synthetic), (
        "BLANCO_PROFILE_API_BOUNDARY_DETECTOR_FALSE_GREEN: Der Gate-Detektor muss "
        "einen profilfreien Server ohne expliziten API-Guard erkennen."
    )


def test_detector_accepts_explicit_guarded_blanco_contract() -> None:
    synthetic = (
        "PROFILE_ID = None\n"
        "PROFILE_CONTEXT_REQUIRED = 'PROFILE_CONTEXT_REQUIRED'\n"
        "def _require_profile_context():\n"
        "    if not PROFILE_ID:\n"
        "        raise RuntimeError(PROFILE_CONTEXT_REQUIRED)\n"
    )
    assert not _unsafe_blanco_transition(synthetic), (
        "BLANCO_PROFILE_API_BOUNDARY_DETECTOR_FALSE_RED: Ein expliziter zentraler "
        "fail-closed Profilguard muss als vorbereiteter Blanco-Vertrag gelten."
    )


def _run_direct() -> None:
    tests = [
        test_real_blanco_requires_explicit_profile_api_boundary,
        test_detector_rejects_unguarded_synthetic_blanco,
        test_detector_accepts_explicit_guarded_blanco_contract,
    ]
    failed: list[tuple[str, str]] = []
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failed.append((test.__name__, repr(exc)))
            print(f"FAIL {test.__name__}: {exc}")
    print(f"SUMMARY total={len(tests)} passed={len(tests)-len(failed)} failed={len(failed)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    _run_direct()
