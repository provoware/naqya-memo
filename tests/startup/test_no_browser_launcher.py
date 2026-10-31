"""Regression checks for the browserless Linux launcher's port-guard contract."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "STARTEN_OHNE_BROWSER.sh"


def run_launcher(action, exit_code, reason="REQUESTED_PORT_OCCUPIED_STRICT"):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "tools").mkdir()
        (root / "app").mkdir()
        shutil.copyfile(LAUNCHER, root / "STARTEN_OHNE_BROWSER.sh")
        (root / "tools" / "startup_port_guard.py").write_text(
            "import json,sys\n"
            f"print(json.dumps({{'action': {action!r}, 'selected_port': 8765, 'reason': {reason!r}}}))\n"
            f"sys.exit({exit_code})\n", encoding="utf-8"
        )
        (root / "app" / "server.py").write_text(
            "import json,os,sys\n"
            "print(json.dumps({'port':os.environ.get('PROVOWARE_PORT'),"
            "'no_browser':os.environ.get('PROVOWARE_NO_BROWSER'),"
            "'args':sys.argv[1:]}))\n", encoding="utf-8"
        )
        env = os.environ.copy()
        env["PROVOWARE_PORT"] = "8765"
        return subprocess.run(
            ["bash", str(root / "STARTEN_OHNE_BROWSER.sh")],
            cwd=root, env=env, text=True, capture_output=True, timeout=10,
        )


def test_guard_failure_is_visible_and_preserves_exit_status():
    result = run_launcher("ERROR", 98)
    assert result.returncode == 98, result
    assert "Start nicht möglich" in result.stderr, result
    assert "REQUESTED_PORT_OCCUPIED_STRICT" in result.stderr, result
    assert "no_browser" not in result.stdout, result


def test_guard_unexpected_error_preserves_exit_status():
    result = run_launcher("ERROR", 2, "GUARD_INTERNAL_ERROR")
    assert result.returncode == 2, result
    assert "GUARD_INTERNAL_ERROR" in result.stderr, result


def test_successful_start_still_disables_browser():
    result = run_launcher("START", 0, "REQUESTED_PORT_FREE")
    assert result.returncode == 0, result
    payload = json.loads(result.stdout.splitlines()[-1])
    assert payload == {"port": "8765", "no_browser": "1", "args": ["--no-browser"]}, result


if __name__ == "__main__":
    tests = [test_guard_failure_is_visible_and_preserves_exit_status,
             test_guard_unexpected_error_preserves_exit_status,
             test_successful_start_still_disables_browser]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"SUMMARY total={len(tests)} passed={len(tests)} failed=0")
