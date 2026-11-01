"""A fresh soak attempt must invalidate a previous PASS before the first checkpoint.

Synthetic interruption tests only; they are NOT real eight-hour endurance evidence.
"""
import json
import runpy
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / "tools/release_gate/gate_01_8h_soak.py"
GATE = "GATE_01_8H_SOAK"


class SoakStaleEvidenceTests(unittest.TestCase):
    def check_interrupted_start(self, args, expected_status):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            script = root / "tools/release_gate/gate_01_8h_soak.py"
            script.parent.mkdir(parents=True)
            shutil.copyfile(SOURCE, script)
            evidence_path = root / "registry/evidence/v0.12.2/gates" / (GATE + ".json")
            evidence_path.parent.mkdir(parents=True)
            evidence_path.write_text(json.dumps({
                "gate": GATE, "status": "PASS", "qualification": "FULL_8H",
                "required_seconds": 28800, "executed_seconds": 28801,
                "integrity": "ok", "errors": []
            }), encoding="utf-8")

            fake_core = types.ModuleType("provoware_core")

            def interrupt_before_first_checkpoint(*_args, **_kwargs):
                raise KeyboardInterrupt("simulated interrupted storage startup")

            fake_core.CoreStore = interrupt_before_first_checkpoint
            fake_core.MutationQueue = object
            fake_core.MemoService = object
            fake_core.TodoService = object

            with patch.dict(sys.modules, {"provoware_core": fake_core}), \
                 patch.object(sys, "argv", [str(script), *args]):
                with self.assertRaises(KeyboardInterrupt):
                    runpy.run_path(str(script), run_name="__main__")

            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(evidence["gate"], GATE)
            self.assertEqual(evidence["status"], expected_status)
            self.assertEqual(evidence["executed_seconds"], 0)
            self.assertNotEqual(evidence["status"], "PASS")

    def test_interrupted_full_soak_cannot_reuse_previous_pass(self):
        self.check_interrupted_start(["--hours", "8"], "RUNNING")

    def test_interrupted_preflight_cannot_reuse_previous_pass(self):
        self.check_interrupted_start(["--preflight-seconds", "5"], "PRECHECK_RUNNING")


if __name__ == "__main__":
    unittest.main()
