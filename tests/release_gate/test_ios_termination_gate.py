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
    def exercise_gate(self, terminate_code, terminate_error=None, launch_failure_mode=None, listing_code=0, listing_error=None, install_error=None, launch_error_mode=None, listing_text=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "tools/release_gate/gate_07_ios_iphone_x.py"
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            app = root / "Naqya.app"
            app.mkdir()
            stale_gate = root / "registry/evidence/v0.12.2/gates/GATE_07_IOS_IPHONE_X.json"
            stale_gate.parent.mkdir(parents=True)
            stale_gate.write_text('{"status":"PASS","stale":true}', encoding="utf-8")
            calls = []

            def fake_run(args, **_kwargs):
                calls.append(args)
                if "xctrace" in args:
                    if listing_error == "timeout":
                        raise subprocess.TimeoutExpired(args, 20)
                    if listing_error == "oserror":
                        raise OSError("mock xctrace failure")
                    return subprocess.CompletedProcess(args, listing_code, listing_text if listing_text is not None else "iPhone X (16.7.16) (TEST-UDID)\n", "")
                if "terminate" in args:
                    if terminate_error == "timeout":
                        raise subprocess.TimeoutExpired(args, 20)
                    if terminate_error == "oserror":
                        raise OSError("mock xcrun failure")
                    return subprocess.CompletedProcess(args, terminate_code, "", "device termination failed" if terminate_code else "")
                if "install" in args:
                    if install_error == "timeout":
                        raise subprocess.TimeoutExpired(args, 90)
                    if install_error == "oserror":
                        raise OSError("mock install failure")
                return subprocess.CompletedProcess(args, 0, "installed", "")

            class FakeProcess:
                def __init__(self, args, **_kwargs):
                    self.mode = args[-1]
                    calls.append(args)
                    if self.mode == launch_error_mode:
                        raise OSError("mock launch failure")
                    self.returncode = 1 if self.mode == launch_failure_mode else 0

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

    def test_termination_exception_replaces_stale_pass(self):
        for failure in ("timeout", "oserror"):
            with self.subTest(failure=failure):
                code, evidence, calls = self.exercise_gate(0, terminate_error=failure)
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertIn("termination", evidence["reason"].lower())
                self.assertFalse(any(args[-1] == "verify" for args in calls))

    def test_nonzero_launch_exit_cannot_pass_gate(self):
        # A PASS-shaped console line is not trustworthy if devicectl itself failed.
        for failure_mode in ("run", "verify"):
            with self.subTest(failure_mode=failure_mode):
                code, evidence, calls = self.exercise_gate(0, launch_failure_mode=failure_mode)
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertTrue(any(args[-1] == failure_mode for args in calls))
                self.assertEqual(evidence[f"{failure_mode}_exit_code"], 1)
                self.assertIn("failed", evidence["reason"])
                if failure_mode == "run":
                    self.assertFalse(any(args[-1] == "verify" for args in calls))

    def test_install_exception_replaces_stale_pass(self):
        # Installation failures must invalidate any previous successful device evidence.
        for failure in ("timeout", "oserror"):
            with self.subTest(failure=failure):
                code, evidence, calls = self.exercise_gate(0, install_error=failure)
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertIn("installation", evidence["reason"].lower())
                self.assertFalse(any(args[-1] in ("run", "verify") for args in calls))

    def test_successful_termination_preserves_pass_path(self):
        code, evidence, calls = self.exercise_gate(0)
        self.assertEqual(code, 0)
        self.assertEqual(evidence["status"], "PASS")
        self.assertTrue(any(args[-1] == "verify" for args in calls))


    def test_failed_device_listing_cannot_pass_gate(self):
        for code in (1, 2):
            with self.subTest(exit_code=code):
                exit_code, evidence, calls = self.exercise_gate(0, listing_code=code)
                self.assertEqual(exit_code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertIn("device listing", evidence["reason"].lower())
                self.assertFalse(any("install" in args for args in calls))

    def test_device_listing_exception_replaces_stale_pass(self):
        for failure in ("timeout", "oserror"):
            with self.subTest(failure=failure):
                exit_code, evidence, calls = self.exercise_gate(0, listing_error=failure)
                self.assertEqual(exit_code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertIn("device listing", evidence["reason"].lower())
                self.assertFalse(any("install" in args for args in calls))

    def test_device_id_substring_does_not_validate_other_iphone(self):
        # A different device ID containing the requested ID must never prove this device is iPhone X.
        for device_id in ("OTHER-TEST-UDID", "TEST-UDID-EXTRA"):
            with self.subTest(device_id=device_id):
                listing = f"iPhone X (16.7.16) ({device_id})\n"
                code, evidence, calls = self.exercise_gate(0, listing_text=listing)
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertFalse(any("install" in args for args in calls))

    def test_launch_oserror_replaces_stale_pass(self):
        for mode in ("run", "verify"):
            with self.subTest(mode=mode):
                code, evidence, calls = self.exercise_gate(0, launch_error_mode=mode)
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertIn("failed", evidence["reason"].lower())
                self.assertTrue(any(args[-1] == mode for args in calls))


    def test_other_iphone_models_cannot_pass_iphone_x_gate(self):
        # A shared name prefix is not proof that the physical model is iPhone X.
        for model in ("iPhone XS", "iPhone XR", "iPhone XS Max", "iPhone X Pro"):
            with self.subTest(model=model):
                code, evidence, calls = self.exercise_gate(
                    0, listing_text=f"{model} (16.7.16) (TEST-UDID)\n"
                )
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertFalse(any("install" in args for args in calls))

    def test_ios_version_must_match_exactly(self):
        for version in ("16.7.160", "116.7.16", "16.7.16.1"):
            with self.subTest(version=version):
                code, evidence, calls = self.exercise_gate(
                    0, listing_text=f"iPhone X ({version}) (TEST-UDID)\n"
                )
                self.assertEqual(code, 2)
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertNotIn("stale", evidence)
                self.assertFalse(any("install" in args for args in calls))

    def test_named_iphone_x_remains_accepted(self):
        code, evidence, calls = self.exercise_gate(
            0, listing_text="Poppis iPhone X (16.7.16) (TEST-UDID)\n"
        )
        self.assertEqual(code, 0)
        self.assertEqual(evidence["status"], "PASS")
        self.assertTrue(any("install" in args for args in calls))

if __name__ == "__main__":
    unittest.main()
