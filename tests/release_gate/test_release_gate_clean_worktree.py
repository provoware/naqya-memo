from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "release_gate" / "require_clean_worktree.py"
spec = importlib.util.spec_from_file_location("require_clean_worktree", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_fixture() -> Path:
    repo = Path(tempfile.mkdtemp(prefix="naqya-release-worktree-"))
    git(repo, "init")
    git(repo, "config", "user.name", "Naqya Test")
    git(repo, "config", "user.email", "naqya-test@example.invalid")
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "baseline")
    return repo


def test_clean_repository_passes():
    repo = repo_fixture()
    clean, reason, details = module.worktree_clean(repo)
    assert clean is True
    assert reason == "WORKTREE_CLEAN"
    assert details == ""


def test_modified_tracked_file_fails_closed():
    repo = repo_fixture()
    (repo / "tracked.txt").write_text("modified\n", encoding="utf-8")
    clean, reason, details = module.worktree_clean(repo)
    assert clean is False
    assert reason == "WORKTREE_NOT_CLEAN"
    assert "tracked.txt" in details


def test_staged_change_fails_closed():
    repo = repo_fixture()
    (repo / "tracked.txt").write_text("staged\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    clean, reason, details = module.worktree_clean(repo)
    assert clean is False
    assert reason == "WORKTREE_NOT_CLEAN"
    assert "tracked.txt" in details


def test_untracked_file_fails_closed():
    repo = repo_fixture()
    (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")
    clean, reason, details = module.worktree_clean(repo)
    assert clean is False
    assert reason == "WORKTREE_NOT_CLEAN"
    assert "untracked.txt" in details


def test_ignored_file_does_not_dirty_release_source():
    repo = repo_fixture()
    (repo / ".gitignore").write_text("ignored.tmp\n", encoding="utf-8")
    git(repo, "add", ".gitignore")
    git(repo, "commit", "-m", "ignore runtime scratch")
    (repo / "ignored.tmp").write_text("runtime scratch\n", encoding="utf-8")
    clean, reason, details = module.worktree_clean(repo)
    assert clean is True
    assert reason == "WORKTREE_CLEAN"
    assert details == ""


def test_non_repository_fails_closed():
    path = Path(tempfile.mkdtemp(prefix="naqya-release-nongit-"))
    clean, reason, details = module.worktree_clean(path)
    assert clean is False
    assert reason == "WORKTREE_STATE_UNAVAILABLE"
    assert details


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"PASS total={len(tests)}")
