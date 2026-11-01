#!/usr/bin/env python3
"""Isolated regression: screenshots never replace real browser app E2E."""

import json
import os
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
GATE_SOURCE = ROOT / 'tools' / 'release_gate' / 'gate_02_chromium.py'

FAKE_SERVER = '''from http.server import BaseHTTPRequestHandler, HTTPServer
import os
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200); self.end_headers(); self.wfile.write(b'{"ok":true}')
 def log_message(self,*args): pass
HTTPServer(('127.0.0.1', int(os.environ['PROVOWARE_PORT'])), Handler).serve_forever()
'''
FAKE_CHROMIUM = '''#!/usr/bin/env python3
import os,sys
if os.environ.get('FAKE_CHROMIUM_WRITES') == '1':
 from pathlib import Path
 screenshot = next(x.split('=',1)[1] for x in sys.argv if x.startswith('--screenshot='))
 Path(screenshot).write_bytes(b'PNG' + b'X'*1500)
'''

class ChromiumScreenshotFreshnessTests(unittest.TestCase):
    def run_gate(self, writes):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = root / 'tools/release_gate/gate_02_chromium.py'
            gate.parent.mkdir(parents=True)
            gate.write_text(GATE_SOURCE.read_text(encoding='utf-8'), encoding='utf-8')
            server = root / 'app/server.py'
            server.parent.mkdir()
            server.write_text(FAKE_SERVER, encoding='utf-8')
            screenshot = root / 'registry/evidence/v0.12.2/chromium_1366x768.png'
            screenshot.parent.mkdir(parents=True)
            (screenshot.parent / 'gates').mkdir()
            previous = b'PREVIOUS' * 200
            screenshot.write_bytes(previous)
            browser = root / 'bin/chromium'
            browser.parent.mkdir()
            browser.write_text(FAKE_CHROMIUM, encoding='utf-8')
            browser.chmod(0o755)
            env = os.environ.copy()
            env['PATH'] = str(browser.parent) + os.pathsep + env.get('PATH', '')
            env['FAKE_CHROMIUM_WRITES'] = '1' if writes else '0'
            completed = subprocess.run([sys.executable, '-S', str(gate)],
                                       cwd=root, env=env, capture_output=True,
                                       text=True, timeout=20)
            evidence = json.loads((screenshot.parent / 'gates/GATE_02_CHROMIUM.json').read_text())
            return completed.returncode, evidence, screenshot.read_bytes()

    def test_interrupted_attempt_invalidates_previous_pass(self):
        # Reproduces an interruption after the gate starts but before browser launch.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = root / 'tools/release_gate/gate_02_chromium.py'
            gate.parent.mkdir(parents=True)
            gate.write_text(GATE_SOURCE.read_text(encoding='utf-8'), encoding='utf-8')
            evidence = root / 'registry/evidence/v0.12.2/gates/GATE_02_CHROMIUM.json'
            evidence.parent.mkdir(parents=True)
            evidence.write_text('{"gate":"GATE_02_CHROMIUM","status":"PASS","stale":true}', encoding='utf-8')
            with patch('shutil.which', return_value='/mock/chromium'), \
                 patch('subprocess.Popen', side_effect=KeyboardInterrupt('simulated interruption')):
                with self.assertRaises(KeyboardInterrupt):
                    runpy.run_path(str(gate), run_name='__main__')
            result = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(result['gate'], 'GATE_02_CHROMIUM')
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertNotIn('stale', result)

    def test_stale_screenshot_does_not_pass(self):
        code, evidence, image = self.run_gate(writes=False)
        self.assertEqual(code, 2)
        self.assertEqual(evidence['status'], 'BLOCKED')
        self.assertEqual(image, b'PREVIOUS' * 200)

    def test_fresh_screenshot_is_only_precheck_not_real_e2e(self):
        code, evidence, image = self.run_gate(writes=True)
        self.assertEqual(code, 2)
        self.assertEqual(evidence['status'], 'PRECHECK_PASS')
        self.assertIn('E2E', evidence['reason'])
        self.assertEqual(image, b'PNG' + b'X' * 1500)

if __name__ == '__main__':
    unittest.main()
