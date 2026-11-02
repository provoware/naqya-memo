"""A cancelled Firefox precheck must never reuse an older real-browser PASS.

Synthetic interruption fixtures only; not real Firefox E2E evidence.
"""
import contextlib
import io
import json
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'tools/release_gate/gate_03_firefox.py'
GATE = 'GATE_03_FIREFOX'


class FirefoxStaleEvidenceTests(unittest.TestCase):
    def exercise(self, interruption):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            script = root / 'tools/release_gate/gate_03_firefox.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            evidence = root / 'registry/evidence/v0.12.2/gates' / (GATE + '.json')
            evidence.parent.mkdir(parents=True)
            evidence.write_text(json.dumps({'gate': GATE, 'status': 'PASS', 'stale': True}), encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                if interruption == 'which':
                    with patch('shutil.which', side_effect=KeyboardInterrupt('simulated interruption')):
                        with self.assertRaises(KeyboardInterrupt):
                            runpy.run_path(str(script), run_name='__main__')
                else:
                    with patch('shutil.which', return_value='/usr/bin/firefox'), patch('subprocess.run', side_effect=KeyboardInterrupt('simulated interruption')):
                        with self.assertRaises(KeyboardInterrupt):
                            runpy.run_path(str(script), run_name='__main__')
            data = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(data['gate'], GATE)
            self.assertEqual(data['status'], 'BLOCKED')
            self.assertNotIn('stale', data)
            self.assertIn('E2E', data['reason'])

    def test_interrupted_executable_lookup_invalidates_old_pass(self):
        self.exercise('which')

    def test_interrupted_version_probe_invalidates_old_pass(self):
        self.exercise('run')

    def test_missing_firefox_stays_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            script = root / 'tools/release_gate/gate_03_firefox.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            evidence = root / 'registry/evidence/v0.12.2/gates' / (GATE + '.json')
            with contextlib.redirect_stdout(io.StringIO()), patch('shutil.which', return_value=None):
                with self.assertRaises(SystemExit) as exc:
                    runpy.run_path(str(script), run_name='__main__')
            self.assertEqual(exc.exception.code, 2)
            self.assertEqual(json.loads(evidence.read_text(encoding='utf-8'))['status'], 'BLOCKED')


if __name__ == '__main__':
    unittest.main()
