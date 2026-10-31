"""Android device gate must invalidate stale PASS before any ADB interaction."""
import contextlib
import io
import json
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

            def fake_adb(args, **kwargs):
                if failure == 'interrupt':
                    raise KeyboardInterrupt('simulated interrupted device listing')
                if failure == 'timeout':
                    raise subprocess.TimeoutExpired(args, 8)
                return subprocess.CompletedProcess(args, 1, '', 'ADB device listing failed')

            with patch('shutil.which', return_value='/usr/bin/adb'), \
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


if __name__ == '__main__':
    unittest.main()
