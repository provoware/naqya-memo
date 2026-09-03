from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "app" / "server.py"

FALLBACK_MARKERS = (
    "SELECT id,display_name FROM profiles WHERE status='ACTIVE' ORDER BY created_at LIMIT 1",
    "profile_service.create('Standardprofil', '0000')",
)

PROFILE_CONTEXT_ERROR = "PROFILE_CONTEXT_REQUIRED"
PROFILE_CONTEXT_GUARD = "_require_profile_context"


def _has_implicit_profile_fallback(source: str) -> bool:
    return any(marker in source for marker in FALLBACK_MARKERS)


def _is_profile_context_error_assignment(node: ast.AST) -> bool:
    if not isinstance(node, (ast.Assign, ast.AnnAssign)):
        return False
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    value = node.value
    if not isinstance(value, ast.Constant) or value.value != PROFILE_CONTEXT_ERROR:
        return False
    return any(isinstance(target, ast.Name) and target.id == PROFILE_CONTEXT_ERROR for target in targets)


def _guard_raises_profile_context_error(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for child in ast.walk(node):
        if not isinstance(child, ast.Raise) or child.exc is None:
            continue
        for exc_part in ast.walk(child.exc):
            if isinstance(exc_part, ast.Name) and exc_part.id == PROFILE_CONTEXT_ERROR:
                return True
            if isinstance(exc_part, ast.Constant) and exc_part.value == PROFILE_CONTEXT_ERROR:
                return True
    return False


def _has_explicit_profile_api_boundary(source: str) -> bool:
    """Recognize executable structure, not comments or inert string markers.

    Before real Blanco runtime the server must define a stable error constant and
    one named guard function whose raise path references that constant. AST-based
    recognition prevents comments, docstrings or unrelated string literals from
    turning the release gate falsely green.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    has_error_constant = any(_is_profile_context_error_assignment(node) for node in tree.body)
    guard = next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == PROFILE_CONTEXT_GUARD
        ),
        None,
    )
    return bool(has_error_constant and guard and _guard_raises_profile_context_error(guard))


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


def test_detector_rejects_marker_only_false_green() -> None:
    synthetic = (
        "PROFILE_ID = None\n"
        "# PROFILE_CONTEXT_REQUIRED\n"
        "# def _require_profile_context(): pass\n"
        "DOC = '_require_profile_context PROFILE_CONTEXT_REQUIRED'\n"
    )
    assert _unsafe_blanco_transition(synthetic), (
        "BLANCO_PROFILE_API_BOUNDARY_MARKER_FALSE_GREEN: Kommentare oder inerte "
        "Strings dürfen keinen ausführbaren Profilkontext-Guard vortäuschen."
    )


def test_detector_accepts_explicit_guarded_blanco_contract() -> None:
    synthetic = (
        "PROFILE_ID = None\n"
        "PROFILE_CONTEXT_REQUIRED = 'PROFILE_CONTEXT_REQUIRED'\n"
        "def _require_profile_context():\n"
        "    if not PROFILE_ID:\n"
        "        raise RuntimeError(PROFILE_CONTEXT_REQUIRED)\n"
        "    return PROFILE_ID\n"
    )
    assert not _unsafe_blanco_transition(synthetic), (
        "BLANCO_PROFILE_API_BOUNDARY_DETECTOR_FALSE_RED: Ein expliziter zentraler "
        "fail-closed Profilguard muss als vorbereiteter Blanco-Vertrag gelten."
    )


def _run_direct() -> None:
    tests = [
        test_real_blanco_requires_explicit_profile_api_boundary,
        test_detector_rejects_unguarded_synthetic_blanco,
        test_detector_rejects_marker_only_false_green,
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
