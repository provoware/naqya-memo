from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TARGETS = {
    ROOT / "app" / "secure_server.py": {
        "base.PROFILE_ID": {
            "_harden_first_profile_if_needed",
            "_profile_revision",
            "SecureHandler._authorized",
        }
    },
    ROOT / "app" / "secure_response_server.py": {
        "secure.base.PROFILE_ID": {
            "_response_auth_profile_id",
        }
    },
}

# Existing direct dependencies may shrink during the planned centralization, but
# they must never multiply silently inside an already allowlisted scope. Without
# this budget, adding more direct PROFILE_ID reads to one of the known functions
# would bypass the scope-only containment check.
MAX_OCCURRENCES = {
    ROOT / "app" / "secure_server.py": {
        ("base.PROFILE_ID", "_harden_first_profile_if_needed"): 3,
        ("base.PROFILE_ID", "_profile_revision"): 1,
        ("base.PROFILE_ID", "SecureHandler._authorized"): 1,
    },
    ROOT / "app" / "secure_response_server.py": {
        ("secure.base.PROFILE_ID", "_response_auth_profile_id"): 1,
    },
}


class DirectProfileAccessVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.scope: list[str] = []
        self.hits: list[tuple[str, str, int]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Attribute(self, node: ast.Attribute) -> None:
        dotted = _dotted_name(node)
        if dotted and dotted.endswith("PROFILE_ID"):
            scope = ".".join(self.scope) or "<module>"
            self.hits.append((dotted, scope, node.lineno))
        self.generic_visit(node)


def _dotted_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _violations_for_source(
    source: str,
    allowlist: dict[str, set[str]],
    *,
    label: str,
    max_occurrences: dict[tuple[str, str], int] | None = None,
) -> list[str]:
    tree = ast.parse(source, filename=label)
    visitor = DirectProfileAccessVisitor()
    visitor.visit(tree)

    violations: list[str] = []
    allowed_hits: Counter[tuple[str, str]] = Counter()
    for dotted, scope, lineno in visitor.hits:
        allowed_scopes = allowlist.get(dotted)
        if allowed_scopes is None or scope not in allowed_scopes:
            violations.append(f"{label}:{lineno}: {dotted} in {scope}")
            continue
        allowed_hits[(dotted, scope)] += 1

    for key, count in sorted(allowed_hits.items()):
        maximum = (max_occurrences or {}).get(key)
        if maximum is None:
            violations.append(
                f"{label}: {key[0]} in {key[1]} has no occurrence budget"
            )
        elif count > maximum:
            violations.append(
                f"{label}: {key[0]} in {key[1]} occurs {count} times; maximum {maximum}"
            )
    return violations


def _assert_file_contained(path: Path, allowlist: dict[str, set[str]]) -> None:
    violations = _violations_for_source(
        path.read_text(encoding="utf-8"),
        allowlist,
        label=str(path.relative_to(ROOT)),
        max_occurrences=MAX_OCCURRENCES[path],
    )
    assert not violations, (
        "AUTH_PROFILE_DEPENDENCY_SPREAD: Direkte PROFILE_ID-Kopplung hat die bekannte "
        "Auth-Grenze verlassen oder sich innerhalb einer bekannten Grenze vermehrt. "
        "Neue direkte Zugriffe sind im Release-Freeze nicht zulässig; stattdessen den "
        "zentralen Profil/Auth-Grenzpunkt verwenden oder zuerst den Vertrag gezielt "
        "aktualisieren.\n" + "\n".join(violations)
    )


def test_direct_profile_id_dependency_stays_contained() -> None:
    for path, allowlist in TARGETS.items():
        _assert_file_contained(path, allowlist)


def test_response_layer_has_single_profile_resolver_boundary() -> None:
    """The outer response layer may touch PROFILE_ID only in its fail-closed resolver."""
    path = ROOT / "app" / "secure_response_server.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    visitor = DirectProfileAccessVisitor()
    visitor.visit(tree)
    hits = [(dotted, scope) for dotted, scope, _ in visitor.hits]
    assert hits == [("secure.base.PROFILE_ID", "_response_auth_profile_id")], (
        "AUTH_PROFILE_RESPONSE_BOUNDARY_DRIFT: secure_response_server.py muss genau einen "
        "direkten PROFILE_ID-Zugriff besitzen und dieser muss im fail-closed Resolver "
        "_response_auth_profile_id gekapselt bleiben."
    )


def test_detector_rejects_new_direct_profile_id_scope() -> None:
    """Mutation probe: prove the detector catches a newly spread dependency."""
    synthetic = (
        "def accidental_auth_helper():\n"
        "    return base.PROFILE_ID\n"
    )
    secure_server = ROOT / "app" / "secure_server.py"
    violations = _violations_for_source(
        synthetic,
        TARGETS[secure_server],
        label="<mutation-probe-new-scope>",
        max_occurrences=MAX_OCCURRENCES[secure_server],
    )
    assert violations == [
        "<mutation-probe-new-scope>:2: base.PROFILE_ID in accidental_auth_helper"
    ], (
        "AUTH_PROFILE_CONTAINMENT_DETECTOR_FALSE_GREEN: Der Mutationstest konnte eine "
        "absichtlich neu eingeführte direkte PROFILE_ID-Kopplung nicht eindeutig erkennen."
    )


def test_detector_rejects_extra_access_inside_allowed_scope() -> None:
    """Mutation probe: an allowlisted function may not accumulate extra direct reads."""
    synthetic = (
        "def _profile_revision():\n"
        "    first = base.PROFILE_ID\n"
        "    second = base.PROFILE_ID\n"
        "    return first, second\n"
    )
    secure_server = ROOT / "app" / "secure_server.py"
    violations = _violations_for_source(
        synthetic,
        TARGETS[secure_server],
        label="<mutation-probe-allowed-scope-growth>",
        max_occurrences=MAX_OCCURRENCES[secure_server],
    )
    assert violations == [
        "<mutation-probe-allowed-scope-growth>: base.PROFILE_ID in _profile_revision occurs 2 times; maximum 1"
    ], (
        "AUTH_PROFILE_OCCURRENCE_BUDGET_FALSE_GREEN: Der Detektor ließ zusätzliche direkte "
        "PROFILE_ID-Zugriffe innerhalb einer bereits erlaubten Auth-Grenze unbemerkt zu."
    )


if __name__ == "__main__":
    tests = [
        test_direct_profile_id_dependency_stays_contained,
        test_response_layer_has_single_profile_resolver_boundary,
        test_detector_rejects_new_direct_profile_id_scope,
        test_detector_rejects_extra_access_inside_allowed_scope,
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
