#!/usr/bin/env python3
"""Regression contract: Quality test sources must not introduce direct external network clients."""
from __future__ import annotations

import ast
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
TEST_ROOT = ROOT / "tests"
SELF = Path(__file__).resolve()

# Third-party/protocol clients have no accepted role in the frozen Quality test path.
FORBIDDEN_PYTHON_IMPORTS = {
    "aiohttp",
    "ftplib",
    "httpx",
    "requests",
    "smtplib",
    "telnetlib",
    "xmlrpc.client",
}

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "[::1]"}

FORBIDDEN_JS_IMPORT = re.compile(
    r"(?:from\s+|require\(\s*|import\(\s*)['\"](?:node:)?(?:http|https|net|tls|dns|dgram)['\"]"
)
FORBIDDEN_JS_CALL = re.compile(r"\b(?:fetch|WebSocket|XMLHttpRequest)\s*\(")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def constant_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def is_loopback_host(node: ast.AST) -> bool:
    value = constant_string(node)
    return value is not None and value.lower() in LOOPBACK_HOSTS


def is_loopback_url(node: ast.AST) -> bool:
    value = constant_string(node)
    if value is None:
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return (parsed.hostname or "").lower() in {"127.0.0.1", "localhost", "::1"}


def is_loopback_socket_target(node: ast.AST) -> bool:
    if isinstance(node, (ast.Tuple, ast.List)) and node.elts:
        return is_loopback_host(node.elts[0])
    return False


def check_python(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{path.relative_to(ROOT)}: cannot parse safely: {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_PYTHON_IMPORTS:
                    findings.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: forbidden external-client import {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FORBIDDEN_PYTHON_IMPORTS:
                findings.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: forbidden external-client import {module}"
                )
        elif isinstance(node, ast.Call):
            name = dotted_name(node.func)
            if name in {"http.client.HTTPConnection", "http.client.HTTPSConnection"}:
                if not node.args or not is_loopback_host(node.args[0]):
                    findings.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: {name} target is not a literal loopback host"
                    )
            elif name == "urllib.request.urlopen":
                if not node.args or not is_loopback_url(node.args[0]):
                    findings.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: urllib.request.urlopen target is not a literal loopback URL"
                    )
            elif name == "socket.create_connection":
                if not node.args or not is_loopback_socket_target(node.args[0]):
                    findings.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: socket.create_connection target is not a literal loopback endpoint"
                    )
    return findings


def check_javascript(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [f"{path.relative_to(ROOT)}: cannot read safely: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if FORBIDDEN_JS_IMPORT.search(stripped):
            findings.append(
                f"{path.relative_to(ROOT)}:{line_number}: direct Node network module import requires explicit review"
            )
        if FORBIDDEN_JS_CALL.search(stripped):
            findings.append(
                f"{path.relative_to(ROOT)}:{line_number}: direct browser/network client call requires explicit review"
            )
    return findings


def main() -> None:
    candidates = sorted(
        path
        for path in TEST_ROOT.rglob("*")
        if path.is_file() and path.resolve() != SELF and path.suffix in {".py", ".js", ".mjs", ".cjs"}
    )
    if not candidates:
        fail("no test-source files found; contract cannot prove its boundary")

    findings: list[str] = []
    python_count = 0
    javascript_count = 0
    for path in candidates:
        if path.suffix == ".py":
            python_count += 1
            findings.extend(check_python(path))
        else:
            javascript_count += 1
            findings.extend(check_javascript(path))

    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        raise SystemExit(1)

    print(
        f"PASS: scanned {len(candidates)} test-source files "
        f"({python_count} Python, {javascript_count} JavaScript)"
    )
    print("PASS: direct Python clients are absent or statically constrained to literal loopback endpoints")
    print("PASS: no direct JavaScript/Node network client is present in Quality test sources")
    print("NOTE: this is a source-level guard, not an OS-level network sandbox")


if __name__ == "__main__":
    main()
