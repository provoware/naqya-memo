"""Android device gate must invalidate stale PASS before any ADB interaction."""
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

SOURCE = Path(__file__).resolve().parents[2] / 'tools/release_gate/gate_06_android_device.py'


class AndroidEvidenceInvalidationTests(unittest.TestCase):
    def exercise(self, failure):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / 'tools/release_gate/gate_06_android_device.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            evidence = root / 'registry/evidence/v0.12.2/gates/GATE_06_ANDROID_DEVICE.json'
            evidence.parent.mkdir(parents=True)
            evidence.write_text('{"gate":"GATE_06_ANDROID_DEVICE","status":"PASS","stale":true}', encoding='utf-8')

            acceptance_apk = root / 'acceptance.apk'
            release_apk = root / 'release.apk'
            acceptance_apk.touch()
            release_apk.touch()

            def fake_adb(args, **kwargs):
                if failure == 'interrupt':
                    raise KeyboardInterrupt('simulated interrupted device listing')
                if failure == 'timeout':
                    raise subprocess.TimeoutExpired(args, 8)
                return subprocess.CompletedProcess(args, 1, '', 'ADB device listing failed')

            with patch.dict(os.environ, {'PROVOWARE_ANDROID_ACCEPTANCE_APK': str(acceptance_apk), 'PROVOWARE_ANDROID_RELEASE_APK': str(release_apk)}), \
                 patch('shutil.which', return_value='/usr/bin/adb'), \
                 patch('subprocess.run', side_effect=fake_adb), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises((KeyboardInterrupt, SystemExit)) as caught:
                    runpy.run_path(str(script), run_name='__main__')
            data = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(data['gate'], 'GATE_06_ANDROID_DEVICE')
            self.assertEqual(data['status'], 'BLOCKED')
            self.assertNotIn('stale', data)
            if failure == 'interrupt':
                self.assertIsInstance(caught.exception, KeyboardInterrupt)
            else:
                self.assertIsInstance(caught.exception, SystemExit)
                self.assertEqual(caught.exception.code, 2)
                self.assertIn('device listing failed', data['reason'])

    def test_interrupted_adb_listing_invalidates_old_pass(self):
        self.exercise('interrupt')

    def test_adb_timeout_is_blocked_and_invalidates_old_pass(self):
        self.exercise('timeout')

    def test_adb_error_exit_is_blocked_and_invalidates_old_pass(self):
        self.exercise('nonzero')



class AndroidResetPreconditionTests(unittest.TestCase):
    """A failed isolation step must not turn old app data or logs into a real PASS."""

    def exercise(self, failed_step):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / 'tools/release_gate/gate_06_android_device.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            acceptance_apk = root / 'acceptance.apk'
            release_apk = root / 'release.apk'
            acceptance_apk.touch()
            release_apk.touch()
            calls = []
            cleared_logs = 0
            read_logs = 0

            def fake_adb(args, **kwargs):
                nonlocal cleared_logs, read_logs
                calls.append(args)
                if args == ['/usr/bin/adb', 'devices']:
                    return subprocess.CompletedProcess(args, 0, 'List of devices attached\nserial-1\tdevice\n', '')
                command = args[3:]
                if command == ['shell', 'getprop', 'ro.product.model']:
                    return subprocess.CompletedProcess(args, 0, 'Pixel 8\n', '')
                if command == ['shell', 'getprop', 'ro.build.version.sdk']:
                    return subprocess.CompletedProcess(args, 0, '34\n', '')
                if command[:3] == ['shell', 'pm', 'clear']:
                    if failed_step == 'app_data':
                        return subprocess.CompletedProcess(args, 1, 'Failed\n', '')
                    return subprocess.CompletedProcess(args, 0, 'Success\n', '')
                if command[:3] == ['shell', 'am', 'force-stop'] and failed_step == 'force_stop':
                    return subprocess.CompletedProcess(args, 1, '', 'Device disconnected')
                if command == ['logcat', '-c']:
                    cleared_logs += 1
                    if (failed_step == 'run_logs' and cleared_logs == 1) or (
                        failed_step == 'verify_logs' and cleared_logs == 2
                    ):
                        return subprocess.CompletedProcess(args, 1, '', 'Log clear failed')
                if command[:3] == ['shell', 'dumpsys', 'package']:
                    return subprocess.CompletedProcess(args, 0, 'versionName=0.12.2\n', '')
                if command[:2] == ['logcat', '-d']:
                    read_logs += 1
                    mode = 'run' if read_logs == 1 else 'verify'
                    logs = 'I/ProvowareAcceptance: {"mode":"' + mode + '","status":"PASS"}\nREMINDER_FIRED:1\n'
                    return subprocess.CompletedProcess(args, 0, logs, '')
                if command[:2] == ['shell', 'pidof']:
                    return subprocess.CompletedProcess(args, 0, '1234\n', '')
                return subprocess.CompletedProcess(args, 0, 'Success\n', '')

            with patch.dict(os.environ, {
                'PROVOWARE_ANDROID_ACCEPTANCE_APK': str(acceptance_apk),
                'PROVOWARE_ANDROID_RELEASE_APK': str(release_apk),
            }), patch('shutil.which', return_value='/usr/bin/adb'), \
                 patch('subprocess.run', side_effect=fake_adb), \
                 patch('time.sleep', return_value=None), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    runpy.run_path(str(script), run_name='__main__')

            evidence = root / 'registry/evidence/v0.12.2/gates/GATE_06_ANDROID_DEVICE.json'
            data = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(data['status'], 'BLOCKED')
            self.assertNotIn('release_pid', data)
            self.assertFalse(any('release.apk' in str(call) for call in calls))
            return data['reason']

    def test_app_data_clear_failure_blocks_gate(self):
        self.assertIn('app data', self.exercise('app_data'))

    def test_run_log_clear_failure_blocks_gate(self):
        self.assertIn('logcat', self.exercise('run_logs'))

    def test_force_stop_failure_blocks_gate(self):
        self.assertIn('force-stopped', self.exercise('force_stop'))

    def test_verify_log_clear_failure_blocks_gate(self):
        self.assertIn('logcat', self.exercise('verify_logs'))


if __name__ == '__main__':
    unittest.main()
