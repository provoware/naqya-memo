"""A new microphone gate run must invalidate an earlier PASS before probing hardware."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'tools/release_gate/gate_04_linux_microphone.py'


class MicrophoneEvidenceInvalidationTests(unittest.TestCase):
    def exercise(self, failure):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / 'tools/release_gate/gate_04_linux_microphone.py'
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            evidence = root / 'registry/evidence/v0.12.2/gates/GATE_04_LINUX_MICROPHONE.json'
            evidence.parent.mkdir(parents=True)
            evidence.write_text('{"gate":"GATE_04_LINUX_MICROPHONE","status":"PASS","stale":true}', encoding='utf-8')

            if failure != 'import':
                package = root / 'core/reference_python/provoware_core'
                package.mkdir(parents=True)
                (package / '__init__.py').write_text('', encoding='utf-8')
                (package / 'assets.py').write_text('class AssetManager: pass\n', encoding='utf-8')
                (package / 'media.py').write_text('class LinuxAudioRecorder: pass\nclass RecordingError(Exception): pass\n', encoding='utf-8')

            with contextlib.redirect_stdout(io.StringIO()), patch.object(sys, 'path', sys.path.copy()):
                if failure == 'import':
                    with patch.dict(sys.modules, {'provoware_core': None}):
                        with self.assertRaises(ModuleNotFoundError):
                            runpy.run_path(str(script), run_name='__main__')
                else:
                    with patch('shutil.which', side_effect=KeyboardInterrupt('simulated interruption')):
                        with self.assertRaises(KeyboardInterrupt):
                            runpy.run_path(str(script), run_name='__main__')

            data = json.loads(evidence.read_text(encoding='utf-8'))
            self.assertEqual(data['gate'], 'GATE_04_LINUX_MICROPHONE')
            self.assertEqual(data['status'], 'BLOCKED')
            self.assertNotIn('stale', data)
            self.assertIn('fresh capture pending', data['reason'])

    def test_import_failure_invalidates_old_pass(self):
        self.exercise('import')

    def test_interrupted_hardware_probe_invalidates_old_pass(self):
        self.exercise('interrupt')


if __name__ == '__main__':
    unittest.main()
