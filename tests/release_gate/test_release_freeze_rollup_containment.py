#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUALIFIED_SOURCE_HEAD = "052a396cd7581de1a0a92dbe152c44b9276ea9d3"
ALLOWED_POST_QUALIFICATION_PATHS = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".github/workflows/quality.yml",
    "docs/release_gate/RELEASE_FREEZE_ROLLUP__STATUS-AKTIV.md",
    "registry/evidence/security/RELEASE_FREEZE_ROLLUP_CONTAINMENT_ACCEPTANCE.json",
    "tests/release_gate/test_release_freeze_rollup_containment.py",
    "tests/ui_consistency/test_v01224_ux_control_plane.py",
    "tests/ui_consistency/test_v01225_real_viewport_ux.py",
}


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    shallow = git("rev-parse", "--is-shallow-repository").stdout.strip().lower()
    if shallow != "false":
        fail("rollup containment requires complete Git history (checkout fetch-depth: 0)")

    if git("cat-file", "-e", f"{QUALIFIED_SOURCE_HEAD}^{{commit}}", check=False).returncode != 0:
        fail(f"qualified source head is unavailable: {QUALIFIED_SOURCE_HEAD}")

    ancestor = git("merge-base", "--is-ancestor", QUALIFIED_SOURCE_HEAD, "HEAD", check=False)
    if ancestor.returncode != 0:
        fail(f"qualified source head is not an ancestor of HEAD: {QUALIFIED_SOURCE_HEAD}")

    status_lines = [
        line for line in git("diff", "--name-status", f"{QUALIFIED_SOURCE_HEAD}..HEAD").stdout.splitlines()
        if line.strip()
    ]
    if not status_lines:
        fail("no post-qualification rollup delta found")

    seen_paths: set[str] = set()
    unexpected: list[str] = []
    destructive: list[str] = []
    for line in status_lines:
        parts = line.split("\t")
        status = parts[0]
        paths = parts[1:]
        if status.startswith(("D", "R", "C")):
            destructive.append(line)
        for path in paths:
            seen_paths.add(path)
            if path not in ALLOWED_POST_QUALIFICATION_PATHS:
                unexpected.append(line)

    if destructive:
        fail("destructive/renaming post-qualification delta detected: " + "; ".join(destructive))
    if unexpected:
        fail("unexpected post-qualification path detected: " + "; ".join(unexpected))

    required = ALLOWED_POST_QUALIFICATION_PATHS
    missing = sorted(required - seen_paths)
    if missing:
        fail("expected rollup process paths missing from qualified delta: " + ", ".join(missing))

    commits = int(git("rev-list", "--count", f"{QUALIFIED_SOURCE_HEAD}..HEAD").stdout.strip())
    if commits < 1:
        fail("rollup HEAD must contain at least one commit after the qualified source head")

    print(
        "PASS: qualified source head is retained as an ancestor; "
        f"{commits} post-qualification commit(s) touch only {len(seen_paths)} approved release-process path(s)."
    )


if __name__ == "__main__":
    main()
