#!/usr/bin/env python3
"""Regression contract: Quality test sources must not silently expand direct network capability."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TEST_ROOT = ROOT / "tests"
SELF = Path(__file__).resolve()

# Existing security regressions intentionally exercise the local desktop server over
# loopback. During release freeze their exact source is treated as an immutable
# reviewed baseline. Any edit to one of these files fails closed until this map is
# deliberately reviewed and updated.
REVIEWED_SECURITY_BASELINE = {
    "tests/security/test_desktop_auth_cache_credential_fingerprint.py": "96d508a6d6d37829e51e37156a2e3440069d00f6",
    "tests/security/test_desktop_auth_cache_profile_incarnation.py": "016433f14122811be6cc5b70eb98c3020625baab",
    "tests/security/test_desktop_auth_cache_revision.py": "6365e0ce3df15aad3a00418a8361b22232cc5da8",
    "tests/security/test_desktop_auth_cache_uncertainty_eviction.py": "0bc51290bbe35504b325c7b77b912343e2469833",
    "tests/security/test_desktop_auth_config_parse.py": "d8ece562f05f932e296a9bfbadf4f76aac09c3a4",
    "tests/security/test_desktop_auth_read_connection.py": "f2dcb9487d34bd2bcb13fd7d568ba64f2b137b46",
    "tests/security/test_desktop_json_body_limit.py": "3790c08cb5b548de2d686835a654f7f83c90e29e",
    "tests/security/test_desktop_pin_gate.py": "5f0f2c92c26215ca136b5df28fb44e79e9fbd50e",
    "tests/security/test_desktop_request_io_timeout.py": "0567f83812c01106ab0843457f50e72a29e2da4d",
    "tests/security/test_desktop_response_headers.py": "8149521bf6189e410512e0c1802a4d3ad5e36082",
    "tests/security/test_desktop_security_config_parse.py": "156895a70962b1d25c58d2650074a5632ec8baa0",
    "tests/security/test_desktop_transport_trust.py": "a291f6236f40c1b1620a68ad3a854be49d15a75e",
    "tests/security/test_desktop_upload_config_parse.py": "15717f17fa2e549b380e80dd77d7ae01a64a79cf",
    "tests/security/test_existing_db_preflight_fail_closed.py": "2f8e054294c3b862eacc3f9738222e92af026d2c",
    "tests/security/test_first_pin_file_symlink_guard.py": "9e865b8f77535aca9263c0a9b4333af733f5d49c",
}

FORBIDDEN_PYTHON_IMPORTS = {
    "aiohttp",
    "ftplib",
    "http.client",
    "httpx",
    "requests",
    "smtplib",
    "socket",
    "telnetlib",
    "urllib.request",
    "xmlrpc.client",
}

FORBIDDEN_PYTHON_CALL_PREFIXES = (
    "socket.",
    "urllib.request.",
    "http.client.",
)

FORBIDDEN_JS_IMPORT = re.compile(
    r"(?:from\s+|require\(\s*|import\(\s*)['\"](?:node:)?(?:http|https|net|tls|dns|dgram)['\"]"
)
FORBIDDEN_JS_CALL = re.compile(r"\b(?:fetch|WebSocket|XMLHttpRequest)\s*\(")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    payload = f"blob {len(data)}\0".encode("ascii") + data
    return hashlib.sha1(payload).hexdigest()


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def verify_reviewed_baseline() -> set[Path]:
    reviewed: set[Path] = set()
    for relative, expected in sorted(REVIEWED_SECURITY_BASELINE.items()):
        path = ROOT / relative
        if not path.is_file():
            fail(f"reviewed security baseline file missing: {relative}")
        actual = git_blob_sha(path)
        if actual != expected:
            fail(
                f"reviewed security baseline drift: {relative} "
                f"expected={expected} actual={actual}"
            )
        reviewed.add(path.resolve())
    return reviewed


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
                        f"{path.relative_to(ROOT)}:{node.lineno}: direct network-capable import {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FORBIDDEN_PYTHON_IMPORTS:
                findings.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: direct network-capable import {module}"
                )
        elif isinstance(node, ast.Call):
            name = dotted_name(node.func) or ""
            if name.startswith(FORBIDDEN_PYTHON_CALL_PREFIXES):
                findings.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: direct network-capable call {name}"
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
                f"{path.relative_to(ROOT)}:{line_number}: direct Node network module import"
            )
        if FORBIDDEN_JS_CALL.search(stripped):
            findings.append(
                f"{path.relative_to(ROOT)}:{line_number}: direct browser/network client call"
            )
    return findings


def main() -> None:
    reviewed = verify_reviewed_baseline()
    candidates = sorted(
        path
        for path in TEST_ROOT.rglob("*")
        if path.is_file()
        and path.resolve() != SELF
        and path.resolve() not in reviewed
        and path.suffix in {".py", ".js", ".mjs", ".cjs"}
    )
    if not candidates:
        fail("no non-baseline test-source files found; contract cannot prove expansion boundary")

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

    print(f"PASS: verified {len(reviewed)} immutable reviewed security-test baseline files")
    print(
        f"PASS: scanned {len(candidates)} remaining test-source files "
        f"({python_count} Python, {javascript_count} JavaScript)"
    )
    print("PASS: no direct network capability was introduced outside the reviewed baseline")
    print("NOTE: source-level expansion guard only; not an OS-level egress sandbox")


if __name__ == "__main__":
    main()
