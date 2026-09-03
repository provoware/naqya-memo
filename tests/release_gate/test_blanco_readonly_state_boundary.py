from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "app" / "server.py"
STATE_PATH = "/api/state"
GUARD = "_require_profile_context"
BLANCO_STATE = "_blanco_api_state"
ALLOWED_TOP_LEVEL_KEYS = {"version", "profile", "readiness"}
ALLOWED_READINESS_KEYS = {"state", "profile_required"}


def _handler_get(tree: ast.Module):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Handler":
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "do_GET":
                    return child
    return None


def _calls(node: ast.AST, name: str) -> bool:
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id == name
        for child in ast.walk(node)
    )


def _api_guard_covers_state(source: str, tree: ast.Module) -> bool:
    method = _handler_get(tree)
    if method is None:
        return False
    for node in method.body:
        if not isinstance(node, ast.Try):
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.If) or not _calls(stmt, GUARD):
                continue
            condition = ast.get_source_segment(source, stmt.test) or ""
            if "path.startswith('/api/')" in condition or 'path.startswith("/api/")' in condition:
                # An explicit state-path exception means the generic guard no longer covers it.
                return STATE_PATH not in condition
    return False


def _blanco_state_helper(tree: ast.Module):
    return next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == BLANCO_STATE
        ),
        None,
    )


def _dict_items(node: ast.Dict) -> dict[str, ast.AST] | None:
    result: dict[str, ast.AST] = {}
    for key, value in zip(node.keys, node.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            return None
        result[key.value] = value
    return result


def _helper_has_allowlisted_shape(helper: ast.AST | None) -> bool:
    if helper is None:
        return False
    returns = [node for node in ast.walk(helper) if isinstance(node, ast.Return)]
    if len(returns) != 1 or not isinstance(returns[0].value, ast.Dict):
        return False

    payload = _dict_items(returns[0].value)
    if payload is None or set(payload) != ALLOWED_TOP_LEVEL_KEYS:
        return False
    if not isinstance(payload["version"], ast.Name) or payload["version"].id != "APP_VERSION":
        return False
    if not isinstance(payload["profile"], ast.Constant) or payload["profile"].value is not None:
        return False

    readiness = payload["readiness"]
    if not isinstance(readiness, ast.Dict):
        return False
    readiness_payload = _dict_items(readiness)
    if readiness_payload is None or set(readiness_payload) != ALLOWED_READINESS_KEYS:
        return False
    state = readiness_payload["state"]
    profile_required = readiness_payload["profile_required"]
    if not isinstance(state, ast.Constant) or state.value != "PROFILE_REQUIRED":
        return False
    if not isinstance(profile_required, ast.Constant) or profile_required.value is not True:
        return False

    # Neutral state must never query profile-bound services, DB/store, assets, queue,
    # memo/todo/calendar helpers, or the rich api_state payload.
    forbidden_names = {
        "store", "settings_service", "memo_service", "todo_service", "calendar_service",
        "asset_manager", "audio_recorder", "playlist_service", "reminder_engine", "queue",
        "api_state", "entity_list", "colors", "day_colors", "backup_status",
    }
    return not any(isinstance(node, ast.Name) and node.id in forbidden_names for node in ast.walk(helper))


def _state_dispatch_calls_blanco_helper(tree: ast.Module) -> bool:
    method = _handler_get(tree)
    if method is None:
        return False
    for node in ast.walk(method):
        if not isinstance(node, ast.If):
            continue
        condition = ast.dump(node.test, include_attributes=False)
        if STATE_PATH in condition and _calls(node, BLANCO_STATE):
            return True
    return False


def _safe_state_boundary(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    if _api_guard_covers_state(source, tree):
        return True
    helper = _blanco_state_helper(tree)
    return _helper_has_allowlisted_shape(helper) and _state_dispatch_calls_blanco_helper(tree)


def _assert_valid_synthetic(source: str) -> None:
    """Ensure mutation fixtures exercise the semantic detector, not SyntaxError fallback."""
    ast.parse(source)


def test_current_server_keeps_state_guarded_or_explicitly_neutral() -> None:
    source = SERVER.read_text(encoding="utf-8")
    assert _safe_state_boundary(source), (
        "BLANCO_STATE_BOUNDARY_UNSAFE: /api/state darf den Profilguard nur verlassen, "
        "wenn ein expliziter neutraler _blanco_api_state-Vertrag aktiv ist."
    )


def test_detector_rejects_naive_state_exemption() -> None:
    synthetic = """
PROFILE_ID = None

def _require_profile_context():
    return PROFILE_ID

class Handler:
    def do_GET(self):
        path = self.path
        try:
            if path.startswith('/api/') and path != '/api/state':
                _require_profile_context()
            if path == '/api/state':
                return self._ok(api_state())
        except Exception:
            return None
"""
    _assert_valid_synthetic(synthetic)
    assert not _safe_state_boundary(synthetic), (
        "BLANCO_STATE_EXEMPTION_FALSE_GREEN: Ein aus dem Guard ausgenommenes /api/state "
        "darf niemals weiterhin den vollständigen api_state() ausliefern."
    )


def test_detector_rejects_neutral_helper_with_profile_data_access() -> None:
    synthetic = """
def _require_profile_context():
    return None

def _blanco_api_state():
    return {'version': APP_VERSION, 'profile': None, 'readiness': store.integrity_check()}
class Handler:
    def do_GET(self):
        path = self.path
        try:
            if path.startswith('/api/') and path != '/api/state':
                _require_profile_context()
            if path == '/api/state':
                return self._ok(_blanco_api_state())
        except Exception:
            return None
"""
    _assert_valid_synthetic(synthetic)
    assert not _safe_state_boundary(synthetic), (
        "BLANCO_STATE_DATA_LEAK_FALSE_GREEN: Der neutrale Statushelper darf keine "
        "profil-/datengebundenen Services oder Stores abfragen."
    )


def test_detector_rejects_extra_readiness_details() -> None:
    synthetic = """
def _require_profile_context():
    return None

def _blanco_api_state():
    return {
        'version': APP_VERSION,
        'profile': None,
        'readiness': {
            'state': 'PROFILE_REQUIRED',
            'profile_required': True,
            'profile_name': PROFILE_NAME,
            'project_path': str(PROJECT),
        },
    }
class Handler:
    def do_GET(self):
        path = self.path
        try:
            if path.startswith('/api/') and path != '/api/state':
                _require_profile_context()
            if path == '/api/state':
                return self._ok(_blanco_api_state())
        except Exception:
            return None
"""
    _assert_valid_synthetic(synthetic)
    assert not _safe_state_boundary(synthetic), (
        "BLANCO_STATE_READINESS_LEAK_FALSE_GREEN: readiness darf keine zusätzlichen "
        "Profil-, Pfad- oder Laufzeitdetails als Seitenkanal transportieren."
    )


def test_detector_accepts_minimal_neutral_state_contract() -> None:
    synthetic = """
def _require_profile_context():
    return None

def _blanco_api_state():
    return {
        'version': APP_VERSION,
        'profile': None,
        'readiness': {'state': 'PROFILE_REQUIRED', 'profile_required': True},
    }
class Handler:
    def do_GET(self):
        path = self.path
        try:
            if path.startswith('/api/') and path != '/api/state':
                _require_profile_context()
            if path == '/api/state':
                return self._ok(_blanco_api_state())
        except Exception:
            return None
"""
    _assert_valid_synthetic(synthetic)
    assert _safe_state_boundary(synthetic), (
        "BLANCO_STATE_BOUNDARY_FALSE_RED: Ein minimaler, datenfreier Read-only-Status "
        "mit exakt version/profile/readiness muss als sichere Blanco-Grenze gelten."
    )


def _run_direct() -> None:
    tests = [
        test_current_server_keeps_state_guarded_or_explicitly_neutral,
        test_detector_rejects_naive_state_exemption,
        test_detector_rejects_neutral_helper_with_profile_data_access,
        test_detector_rejects_extra_readiness_details,
        test_detector_accepts_minimal_neutral_state_contract,
    ]
    failed = []
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
