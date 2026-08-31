#!/usr/bin/env python3
"""Regression contract: Quality test sources must not introduce direct outbound network clients."""
from __future__ import annotations

import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TEST_ROOT = ROOT / "tests"
SELF = Path(__file__).resolve()

FORBIDDEN_PYTHON_IMPORTS = {
    "aiohttp",
    "ftplib",
    "http.client",
    "httpx",
    "requests",
    "smtplib",
    "telnetlib",
    "urllib.request",
    "xmlrpc.client",
}

FORBIDDEN_PYTHON_CALLS = {
    "socket.create_connection",
    "socket.socket.connect",
    "urllib.request.urlopen",
}

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
                        f"{path.relative_to(ROOT)}:{node.lineno}: forbidden network import {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FORBIDDEN_PYTHON_IMPORTS:
                findings.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: forbidden network import {module}"
                )
        elif isinstance(node, ast.Call):
            name = dotted_name(node.func)
            if name in FORBIDDEN_PYTHON_CALLS:
                findings.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: forbidden network call {name}"
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
                f"{path.relative_to(ROOT)}:{line_number}: forbidden Node network module import"
            )
        if FORBIDDEN_JS_CALL.search(stripped):
            findings.append(
                f"{path.relative_to(ROOT)}:{line_number}: forbidden browser/network client call"
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
    print("PASS: no direct outbound network-client API is present in Quality test sources")
    print("NOTE: this is a source-level guard, not an OS-level network sandbox")


if __name__ == "__main__":
    main()
