#!/usr/bin/env python3
"""Regression contract: Quality CI must not implicitly install/download project dependencies."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"

FORBIDDEN = (
    (re.compile(r"(^|[;&|]\s*)(sudo\s+)?(apt|apt-get|dnf|yum|zypper|pacman|apk)\b"), "system package installation"),
    (re.compile(r"(^|[;&|]\s*)(python\s+-m\s+pip|pip3?|uv\s+pip)\s+(install|sync)\b"), "Python dependency installation"),
    (re.compile(r"(^|[;&|]\s*)(npm\s+(install|ci)|npx\b|yarn\b|pnpm\b|bun\s+(install|x)\b)"), "JavaScript dependency execution/installation"),
    (re.compile(r"(^|[;&|]\s*)(curl|wget)\b"), "direct network download"),
    (re.compile(r"(^|[;&|]\s*)git\s+(submodule\s+(update|init)|lfs\s+(pull|fetch))\b"), "implicit Git dependency/content fetch"),
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def iter_run_lines(text: str):
    lines = text.splitlines()
    in_run = False
    run_indent = 0
    for line_number, raw in enumerate(lines, start=1):
        match = re.match(r"^(\s*)run:\s*\|\s*$", raw)
        if match:
            in_run = True
            run_indent = len(match.group(1))
            continue
        if not in_run:
            continue
        if raw.strip() and len(raw) - len(raw.lstrip()) <= run_indent:
            in_run = False
            continue
        if not raw.strip():
            continue
        yield line_number, raw.strip()


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    checked = 0
    for line_number, command in iter_run_lines(text):
        if command.startswith("#") or command.startswith("echo ") or command.startswith("printf "):
            continue
        checked += 1
        for pattern, reason in FORBIDDEN:
            if pattern.search(command):
                fail(f"{reason} is forbidden in Quality CI at line {line_number}: {command}")

    if checked == 0:
        fail("no executable run-block commands found; parser or workflow contract drift")

    print(f"PASS: checked {checked} Quality CI command lines")
    print("PASS: no implicit package installation, package-runner execution, direct download, or Git dependency fetch")


if __name__ == "__main__":
    main()
