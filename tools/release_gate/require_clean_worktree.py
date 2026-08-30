from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def worktree_clean(root: Path) -> tuple[bool, str, str]:
    """Return whether Git reports no tracked, staged, or untracked worktree changes."""
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "WORKTREE_STATE_UNAVAILABLE", repr(exc)

    dirty = result.stdout.rstrip("\n")
    if dirty:
        return False, "WORKTREE_NOT_CLEAN", dirty
    return True, "WORKTREE_CLEAN", ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail closed unless the release-candidate Git worktree is clean."
    )
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()

    clean, reason, details = worktree_clean(args.root.resolve())
    print(reason)
    if details:
        print(details, file=sys.stderr)
    raise SystemExit(0 if clean else 2)


if __name__ == "__main__":
    main()
