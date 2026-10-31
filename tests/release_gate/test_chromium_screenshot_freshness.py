#!/usr/bin/env python3
"""Isolated regression: only screenshots created by this browser run may pass."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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

    def test_stale_screenshot_does_not_pass(self):
        code, evidence, image = self.run_gate(writes=False)
        self.assertEqual(code, 2)
        self.assertEqual(evidence['status'], 'BLOCKED')
        self.assertEqual(image, b'PREVIOUS' * 200)

    def test_fresh_screenshot_replaces_old_only_on_success(self):
        code, evidence, image = self.run_gate(writes=True)
        self.assertEqual(code, 0)
        self.assertEqual(evidence['status'], 'PASS')
        self.assertEqual(image, b'PNG' + b'X' * 1500)

if __name__ == '__main__':
    unittest.main()
