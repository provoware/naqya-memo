#!/usr/bin/env python3
"""Regression contract: every external GitHub Action in quality.yml is commit-pinned."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"
EXPECTED_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/setup-node",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
USES_LINE = re.compile(r"^\s*uses:\s*([^@\s]+)@([^\s#]+)")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    found = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = USES_LINE.match(line)
        if not match:
            continue
        action, ref = match.groups()
        if action.startswith("./"):
            continue
        if action in found:
            fail(f"duplicate external action {action} at line {line_number}")
        found[action] = (ref, line_number)
        if not SHA40.fullmatch(ref):
            fail(f"mutable or malformed action ref at line {line_number}: {action}@{ref}")

    missing = EXPECTED_ACTIONS - set(found)
    unexpected = set(found) - EXPECTED_ACTIONS
    if missing:
        fail(f"expected external actions missing from workflow: {sorted(missing)}")
    if unexpected:
        fail(f"new external actions require explicit review and contract update: {sorted(unexpected)}")

    if len(found) != len(EXPECTED_ACTIONS):
        fail("external action count drift")

    for action in sorted(found):
        ref, line_number = found[action]
        print(f"PASS: {action} pinned to immutable commit {ref} (line {line_number})")

    print("PASS: quality workflow external-action supply-chain contract")


if __name__ == "__main__":
    main()
