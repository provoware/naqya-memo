from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "RUN_RELEASE_GATE_CLOSURE.sh"


def _fixture(verify_rc: int):
    temp = Path(tempfile.mkdtemp(prefix="naqya-release-runner-verify-"))
    runner = temp / "RUN_RELEASE_GATE_CLOSURE.sh"
    shutil.copy2(RUNNER, runner)
    runner.chmod(0o755)

    manifest = temp / "docs" / "release" / "MOBILE_RUNTIME_RELEASE_MANIFEST.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}\n", encoding="utf-8")

    bin_dir = temp / "bin"
    bin_dir.mkdir()
    log = temp / "calls.log"

    fake_python = bin_dir / "fake-python"
    fake_python.write_text(
        """#!/usr/bin/env sh
if [ \"$1\" = \"-S\" ] && [ \"$2\" = \"-c\" ]; then
  case \"$3\" in
    *datetime*) printf '%s\\n' '2026-08-30T20:00:00+00:00' ;;
    *hashlib*) printf '%064d\\n' 0 | tr ' ' 'f' ;;
    *) exit 2 ;;
  esac
  exit 0
fi
script=\"$2\"
name=$(basename \"$script\")
printf '%s\\n' \"$name\" >> \"$FAKE_LOG\"
if [ \"$name\" = \"verify_release_closure_provenance.py\" ]; then
  exit \"${FAKE_VERIFY_RC:-0}\"
fi
exit 0
""",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    fake_git = bin_dir / "git"
    fake_git.write_text(
        """#!/usr/bin/env sh
case \"$5\" in
  HEAD) printf '%040d\\n' 0 | tr ' ' 'a' ;;
  'HEAD^{tree}') printf '%040d\\n' 0 | tr ' ' 'b' ;;
  *) exit 2 ;;
esac
""",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)

    env = os.environ.copy()
    env["PYTHON"] = str(fake_python)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    env["FAKE_LOG"] = str(log)
    env["FAKE_VERIFY_RC"] = str(verify_rc)
    return temp, runner, log, env


def _run(verify_rc: int):
    temp, runner, log, env = _fixture(verify_rc)
    try:
        result = subprocess.run(
            ["bash", str(runner)],
            cwd=temp,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        calls = log.read_text(encoding="utf-8").splitlines()
        return result, calls
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def test_official_runner_invokes_verifier_after_attestation():
    result, calls = _run(0)
    assert result.returncode == 0, result.stderr
    tail = calls[-3:]
    assert tail == [
        "evaluate_release_gate.py",
        "attest_release_closure.py",
        "verify_release_closure_provenance.py",
    ]


def test_verifier_failure_blocks_official_closure():
    result, calls = _run(7)
    assert "verify_release_closure_provenance.py" in calls
    assert result.returncode == 2


def test_verifier_success_allows_existing_success_path():
    result, _ = _run(0)
    assert result.returncode == 0


def main():
    tests = [
        test_official_runner_invokes_verifier_after_attestation,
        test_verifier_failure_blocks_official_closure,
        test_verifier_success_allows_existing_success_path,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)}/{len(tests)} release closure runner verifier contracts")


if __name__ == "__main__":
    main()
