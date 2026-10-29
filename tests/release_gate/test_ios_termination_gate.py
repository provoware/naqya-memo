"""Isolated iOS gate decision tests; no Xcode or physical device required."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[2] / "tools/release_gate/gate_07_ios_iphone_x.py"


class IOSLifecycleGateTests(unittest.TestCase):
    def exercise_gate(self, terminate_code):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "tools/release_gate/gate_07_ios_iphone_x.py"
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            app = root / "Naqya.app"
            app.mkdir()
            calls = []

            def fake_run(args, **_kwargs):
                calls.append(args)
                if "xctrace" in args:
                    return subprocess.CompletedProcess(args, 0, "iPhone X (16.7.16) (TEST-UDID)\n", "")
                if "terminate" in args:
                    return subprocess.CompletedProcess(args, terminate_code, "", "device termination failed" if terminate_code else "")
                return subprocess.CompletedProcess(args, 0, "installed", "")

            class FakeProcess:
                def __init__(self, args, **_kwargs):
                    self.mode = args[-1]
                    self.returncode = 0
                    calls.append(args)

                def communicate(self, timeout=None):
                    response = f'ProvowareAcceptance {{"mode":"{self.mode}","status":"PASS"}}\n'
                    if self.mode == "run":
                        response += "REMINDER_FIRED: mock\n"
                    return response, None

            with patch.dict(os.environ, {"PROVOWARE_IOS_APP": str(app), "PROVOWARE_IOS_DEVICE_ID": "TEST-UDID"}), \
                 patch("platform.system", return_value="Darwin"), \
                 patch("shutil.which", side_effect=lambda name: "/usr/bin/" + name), \
                 patch("subprocess.run", side_effect=fake_run), \
                 patch("subprocess.Popen", side_effect=FakeProcess), \
                 patch("time.sleep", return_value=None), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as exit_ctx:
                    runpy.run_path(str(script), run_name="__main__")
            evidence = json.loads((root / "registry/evidence/v0.12.2/gates/GATE_07_IOS_IPHONE_X.json").read_text())
            return exit_ctx.exception.code, evidence, calls

    def test_failed_termination_cannot_pass_persistence_gate(self):
        code, evidence, calls = self.exercise_gate(1)
        self.assertEqual(code, 2)
        self.assertEqual(evidence["status"], "BLOCKED")
        self.assertIn("termination", evidence["reason"].lower())
        self.assertFalse(any(args[-1] == "verify" for args in calls))

    def test_successful_termination_preserves_pass_path(self):
        code, evidence, calls = self.exercise_gate(0)
        self.assertEqual(code, 0)
        self.assertEqual(evidence["status"], "PASS")
        self.assertTrue(any(args[-1] == "verify" for args in calls))


if __name__ == "__main__":
    unittest.main()
