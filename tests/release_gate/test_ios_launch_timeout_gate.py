"""Reject console PASS text if an iOS acceptance command timed out."""
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

SOURCE = Path(__file__).resolve().parents[2] / 'tools/release_gate/gate_07_ios_iphone_x.py'


class IOSLaunchTimeoutTests(unittest.TestCase):
    def test_timed_out_console_cannot_prove_acceptance(self):
        for timed_out_mode in ('run', 'verify', None):
            with self.subTest(mode=timed_out_mode), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                script = root / 'tools/release_gate/gate_07_ios_iphone_x.py'
                script.parent.mkdir(parents=True)
                shutil.copyfile(SOURCE, script)
                (root / 'Naqya.app').mkdir()
                evidence_path = root / 'registry/evidence/v0.12.2/gates/GATE_07_IOS_IPHONE_X.json'
                evidence_path.parent.mkdir(parents=True)
                evidence_path.write_text('{"status":"PASS","stale":true}', encoding='utf-8')
                calls = []

                def fake_run(args, **kwargs):
                    calls.append(args)
                    if 'xctrace' in args:
                        return subprocess.CompletedProcess(args, 0, 'iPhone X (16.7.16) (TEST-UDID)\n', '')
                    return subprocess.CompletedProcess(args, 0, 'ok', '')

                class FakeProcess:
                    def __init__(self, args, **kwargs):
                        self.mode = args[-1]
                        self.returncode = 0  # A handler can exit 0 after termination.
                        self.first_call = True
                        calls.append(args)

                    def communicate(self, timeout=None):
                        if self.mode == timed_out_mode and self.first_call:
                            self.first_call = False
                            raise subprocess.TimeoutExpired(['devicectl', self.mode], timeout)
                        text = f'ProvowareAcceptance {{"mode":"{self.mode}","status":"PASS"}}\n'
                        if self.mode == 'run':
                            text += 'REMINDER_FIRED: mock\n'
                        return text, None

                    def terminate(self):
                        calls.append(['terminated', self.mode])

                with patch.dict(os.environ, {'PROVOWARE_IOS_APP': str(root / 'Naqya.app'), 'PROVOWARE_IOS_DEVICE_ID': 'TEST-UDID'}), \
                     patch('platform.system', return_value='Darwin'), \
                     patch('shutil.which', side_effect=lambda name: '/usr/bin/' + name), \
                     patch('subprocess.run', side_effect=fake_run), \
                     patch('subprocess.Popen', side_effect=FakeProcess), \
                     patch('time.sleep', return_value=None), \
                     contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as caught:
                        runpy.run_path(str(script), run_name='__main__')
                evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
                self.assertNotIn('stale', evidence)
                if timed_out_mode is None:
                    self.assertEqual(caught.exception.code, 0)
                    self.assertEqual(evidence['status'], 'PASS')
                    self.assertFalse(any(call[0] == 'terminated' for call in calls))
                else:
                    self.assertEqual(caught.exception.code, 2)
                    self.assertEqual(evidence['status'], 'BLOCKED')
                    self.assertIn('timed out', evidence['reason'])
                    self.assertEqual(evidence[f'{timed_out_mode}_exit_code'], 0)
                    self.assertTrue(any(call == ['terminated', timed_out_mode] for call in calls))
                    if timed_out_mode == 'run':
                        self.assertFalse(any(call[-1] == 'verify' for call in calls))


if __name__ == '__main__':
    unittest.main()
