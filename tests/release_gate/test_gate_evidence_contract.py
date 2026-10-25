"""Regressionen für die kanonische Release-Evidence-Auswertung.

Alle Daten in diesem Test sind synthetische Fixtures, KEINE reale Gate-Evidence.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "release_gate"))
from evidence_contract import GATES, mobile_source_status, read_gate


class EvidenceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.gates = self.root / "registry/evidence/v0.12.2/gates"
        self.gates.mkdir(parents=True)

    def write_gate(self, number, name, status, **extra):
        data = {"gate": f"GATE_{number}_{name}", "status": status, **extra}
        (self.gates / f"GATE_{number}_{name}.json").write_text(json.dumps(data))
        return data

    def test_prefix_decoy_is_ignored(self):
        self.write_gate("01", "8H_SOAK", "PRECHECK_PASS")
        (self.gates / "GATE_01_ZZZ.json").write_text(
            json.dumps({"gate": "GATE_01_ZZZ", "status": "PASS"})
        )
        self.assertEqual(read_gate(self.root, "01", "8H_SOAK")["status"], "PRECHECK_PASS")

    def test_gate_identity_mismatch_is_fail_closed(self):
        self.write_gate("05", "STORAGE_FAILURE", "PASS")
        (self.gates / "GATE_05_STORAGE_FAILURE.json").write_text(
            json.dumps({"gate": "GATE_06_ANDROID_DEVICE", "status": "PASS"})
        )
        self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "INVALID_EVIDENCE")

    def test_short_soak_cannot_be_promoted(self):
        self.write_gate(
            "01", "8H_SOAK", "PASS", qualification="PRECHECK_ONLY",
            required_seconds=28800, executed_seconds=5.02, integrity="ok", errors=[]
        )
        self.assertEqual(read_gate(self.root, "01", "8H_SOAK")["status"], "INVALID_EVIDENCE")

    def test_real_duration_contract_is_structurally_accepted(self):
        self.write_gate(
            "01", "8H_SOAK", "PASS", qualification="FULL_8H",
            required_seconds=28800, executed_seconds=28801, integrity="ok", errors=[]
        )
        self.assertEqual(read_gate(self.root, "01", "8H_SOAK")["status"], "PASS")

    def test_malformed_and_non_object_json_are_invalid(self):
        path = self.gates / "GATE_03_FIREFOX.json"
        path.write_text("{invalid")
        self.assertEqual(read_gate(self.root, "03", "FIREFOX")["status"], "INVALID_EVIDENCE")
        path.write_text('["PASS"]')
        self.assertEqual(read_gate(self.root, "03", "FIREFOX")["status"], "INVALID_EVIDENCE")

    def test_symlink_evidence_is_invalid(self):
        target = self.root / "outside.json"
        target.write_text('{"gate":"GATE_05_STORAGE_FAILURE","status":"PASS"}')
        (self.gates / "GATE_05_STORAGE_FAILURE.json").symlink_to(target)
        self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "INVALID_EVIDENCE")

    def test_invalid_mobile_source_is_not_pass(self):
        source = self.root / "registry/evidence/v0.12.2/MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json"
        source.write_text('["PASS"]')
        self.assertEqual(mobile_source_status(self.root), "INVALID_EVIDENCE")
        source.write_text('{"status":"PASS"}')
        self.assertEqual(mobile_source_status(self.root), "PASS")

    def test_evaluator_counts_only_exact_valid_gates(self):
        scripts = self.root / "tools/release_gate"
        scripts.mkdir(parents=True)
        for filename in ("evaluate_release_gate.py", "evidence_contract.py"):
            shutil.copy2(ROOT / "tools/release_gate" / filename, scripts / filename)
        version = self.root / "registry/VERSION.json"
        version.parent.mkdir(parents=True, exist_ok=True)
        version.write_text('{"version":"TEST-ONLY"}')
        for number, name in GATES:
            self.write_gate(number, name, "BLOCKED")
        self.write_gate("05", "STORAGE_FAILURE", "PASS")
        self.write_gate("01", "8H_SOAK", "PRECHECK_PASS")
        (self.gates / "GATE_01_ZZZ.json").write_text(
            '{"gate":"GATE_01_ZZZ","status":"PASS"}'
        )
        source = self.root / "registry/evidence/v0.12.2/MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json"
        source.write_text('{"status":"PASS"}')
        result = subprocess.run(
            [sys.executable, "-S", str(scripts / "evaluate_release_gate.py")],
            cwd=self.root, capture_output=True, text=True, timeout=10
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads((self.root / "registry/evidence/v0.12.2/RELEASE_GATE_CLOSURE.json").read_text())
        self.assertEqual(output["passed_real_gates"], 1)
        self.assertEqual(output["release_status"], "NO-GO")
        self.assertFalse(output["v1_rc_allowed"])


if __name__ == "__main__":
    unittest.main()
