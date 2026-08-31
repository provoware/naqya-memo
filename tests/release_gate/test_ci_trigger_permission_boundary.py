#!/usr/bin/env python3
"""Regression contract: Quality CI must keep a minimal untrusted-PR trigger/permission boundary."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"

EXPECTED_TRIGGER_BLOCK = """on:
  pull_request:
  push:
    branches:
      - main
"""
EXPECTED_PERMISSIONS_BLOCK = """permissions:
  contents: read
"""
FORBIDDEN_TRIGGERS = (
    "pull_request_target",
    "workflow_run",
    "workflow_call",
    "repository_dispatch",
    "workflow_dispatch",
    "issue_comment",
    "issues",
    "schedule",
)
PRIVILEGED_PERMISSION_NAMES = (
    "actions",
    "attestations",
    "checks",
    "deployments",
    "id-token",
    "issues",
    "packages",
    "pages",
    "pull-requests",
    "repository-projects",
    "security-events",
    "statuses",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def _top_level_block(text: str, key: str) -> str | None:
    lines = text.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if line == f"{key}:\n" or line == f"{key}:\r\n":
            if start is not None:
                fail(f"duplicate top-level {key} block")
            start = index
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].strip() and not lines[index].startswith((" ", "\t")):
            end = index
            break

    # A blank separator line before the next top-level YAML key is formatting,
    # not part of the semantic block. Normalize CRLF and trailing separators so
    # the contract fails only on actual trigger/permission drift.
    block = "".join(lines[start:end]).replace("\r\n", "\n")
    return block.rstrip("\n") + "\n"


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    trigger_block = _top_level_block(text, "on")
    if trigger_block != EXPECTED_TRIGGER_BLOCK:
        fail(f"Quality trigger block drifted from pull_request + push(main) only: {trigger_block!r}")
    for trigger in FORBIDDEN_TRIGGERS:
        if re.search(rf"^\s{{2}}{re.escape(trigger)}\s*:", trigger_block, re.MULTILINE):
            fail(f"privileged or out-of-scope trigger forbidden: {trigger}")

    permissions_block = _top_level_block(text, "permissions")
    if permissions_block != EXPECTED_PERMISSIONS_BLOCK:
        fail(f"Quality permissions must remain exactly contents: read: {permissions_block!r}")

    permission_blocks = re.findall(r"(?m)^\s*permissions\s*:", text)
    if len(permission_blocks) != 1:
        fail(f"expected exactly one permissions block, found {len(permission_blocks)}")

    for permission in PRIVILEGED_PERMISSION_NAMES:
        if re.search(rf"(?m)^\s+{re.escape(permission)}\s*:\s*(write|read)\s*$", text):
            fail(f"unexpected additional permission in Quality workflow: {permission}")

    if re.search(r"(?m)^\s+contents\s*:\s*write\s*$", text):
        fail("contents: write is forbidden in Quality workflow")

    print("PASS: Quality triggers are limited to pull_request and push(main)")
    print("PASS: Quality workflow permissions remain exactly contents: read")
    print("PASS: no job-level or privileged permission expansion detected")


if __name__ == "__main__":
    main()
