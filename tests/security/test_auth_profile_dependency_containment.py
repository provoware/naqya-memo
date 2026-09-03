from __future__ import annotations

import ast
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
            "_profile_security_state_from_readonly_db",
        }
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


def _assert_file_contained(path: Path, allowlist: dict[str, set[str]]) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    visitor = DirectProfileAccessVisitor()
    visitor.visit(tree)

    violations: list[str] = []
    for dotted, scope, lineno in visitor.hits:
        allowed_scopes = allowlist.get(dotted)
        if allowed_scopes is None or scope not in allowed_scopes:
            violations.append(f"{path.relative_to(ROOT)}:{lineno}: {dotted} in {scope}")

    assert not violations, (
        "AUTH_PROFILE_DEPENDENCY_SPREAD: Direkte PROFILE_ID-Kopplung hat die bekannte "
        "Auth-Grenze verlassen. Neue direkte Zugriffe sind im Release-Freeze nicht zulässig; "
        "stattdessen den zentralen Profil/Auth-Grenzpunkt verwenden oder zuerst den Vertrag "
        "gezielt aktualisieren.\n" + "\n".join(violations)
    )


def test_direct_profile_id_dependency_stays_contained() -> None:
    for path, allowlist in TARGETS.items():
        _assert_file_contained(path, allowlist)


if __name__ == "__main__":
    try:
        test_direct_profile_id_dependency_stays_contained()
    except Exception as exc:
        print(f"FAIL test_direct_profile_id_dependency_stays_contained: {exc}")
        raise SystemExit(1)
    print("PASS test_direct_profile_id_dependency_stays_contained")
    print("SUMMARY total=1 passed=1 failed=0")
