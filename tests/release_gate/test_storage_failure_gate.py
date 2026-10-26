#!/usr/bin/env python3
"""Corrupt application evidence must not leave a stale storage-gate PASS."""

import builtins
import contextlib
import errno
import io
import json
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / "tools/release_gate/gate_05_storage_failure.py"


class StorageFailureEvidenceTests(unittest.TestCase):
    def run_gate(self, evidence):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "tools/release_gate/gate_05_storage_failure.py"
            script.parent.mkdir(parents=True)
            script.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
            matrix = root / "registry/evidence/v0.12/FAILURE_MATRIX_RESULTS.json"
            matrix.parent.mkdir(parents=True)
            if evidence is not None:
                matrix.write_text(evidence, encoding="utf-8")
            gate = root / "registry/evidence/v0.12.2/gates/GATE_05_STORAGE_FAILURE.json"
            gate.parent.mkdir(parents=True)
            gate.write_text('{"status":"PASS","old":true}', encoding="utf-8")
            original_open = builtins.open
            original_write_text = Path.write_text

            def fake_open(file, *args, **kwargs):
                if str(file) == "/dev/full":
                    raise OSError(errno.ENOSPC, "Mock disk full")
                return original_open(file, *args, **kwargs)

            def fake_write_text(path, *args, **kwargs):
                if str(path) == "/sys/provoware_rc_write_probe":
                    raise OSError(errno.EROFS, "Mock read-only mount")
                return original_write_text(path, *args, **kwargs)

            with patch("builtins.open", side_effect=fake_open), patch.object(Path, "write_text", fake_write_text):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        runpy.run_path(str(script), run_name="__main__")
            return raised.exception.code, json.loads(gate.read_text(encoding="utf-8"))

    def test_invalid_json_replaces_stale_pass_with_fail(self):
        code, result = self.run_gate('{"broken":')
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["application_failure_matrix_pass"])
        self.assertIn("JSONDecodeError", result["application_failure_matrix_error"])
        self.assertNotIn("old", result)

    def test_missing_matrix_fails_closed(self):
        code, result = self.run_gate(None)
        self.assertEqual(code, 1)
        self.assertFalse(result["application_failure_matrix_evidence_present"])
        self.assertEqual(result["status"], "FAIL")

    def test_valid_matrix_keeps_existing_pass_path(self):
        matrix = json.dumps({
            "disk_full_deterministic_injection": "PASS",
            "permission_denied_deterministic_injection": "PASS",
            "read_only_preflight": "PASS (mocked)",
        })
        code, result = self.run_gate(matrix)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["application_failure_matrix_pass"])


if __name__ == "__main__":
    unittest.main()
