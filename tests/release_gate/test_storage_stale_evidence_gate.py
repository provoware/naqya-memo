#!/usr/bin/env python3
"""Interrupted storage-gate attempts must invalidate an older PASS."""
import builtins
import errno
import json
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / 'tools/release_gate/gate_05_storage_failure.py'
GATE = 'GATE_05_STORAGE_FAILURE'


class StorageGateStartupTests(unittest.TestCase):
    def run_aborted_gate(self, abort_at):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / 'tools/release_gate/gate_05_storage_failure.py'
            script.parent.mkdir(parents=True)
            script.write_text(SOURCE.read_text(encoding='utf-8'), encoding='utf-8')
            evidence = root / 'registry/evidence/v0.12.2/gates' / f'{GATE}.json'
            evidence.parent.mkdir(parents=True)
            evidence.write_text(json.dumps({'gate': GATE, 'status': 'PASS', 'old': True}), encoding='utf-8')
            original_open = builtins.open
            original_write_text = Path.write_text

            def fake_open(file, *args, **kwargs):
                if str(file) == '/dev/full':
                    if abort_at == 'dev_full':
                        raise KeyboardInterrupt('interrupted before kernel probe')
                    raise OSError(errno.ENOSPC, 'simulated full disk')
                return original_open(file, *args, **kwargs)

            def fake_write_text(path, *args, **kwargs):
                if str(path) == '/sys/provoware_rc_write_probe':
                    raise KeyboardInterrupt('interrupted before read-only probe')
                return original_write_text(path, *args, **kwargs)

            with patch('builtins.open', side_effect=fake_open), patch.object(Path, 'write_text', fake_write_text):
                with self.assertRaises(KeyboardInterrupt):
                    runpy.run_path(str(script), run_name='__main__')
            return json.loads(evidence.read_text(encoding='utf-8'))

    def test_abort_before_first_probe_clears_stale_pass(self):
        result = self.run_aborted_gate('dev_full')
        self.assertEqual(result['gate'], GATE)
        self.assertEqual(result['status'], 'RUNNING')
        self.assertNotIn('old', result)

    def test_abort_before_second_probe_clears_stale_pass(self):
        result = self.run_aborted_gate('read_only_mount')
        self.assertEqual(result['gate'], GATE)
        self.assertEqual(result['status'], 'RUNNING')
        self.assertNotIn('old', result)


if __name__ == '__main__':
    unittest.main()
