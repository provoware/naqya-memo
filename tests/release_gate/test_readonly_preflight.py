"""Guardrail: a preflight may not run gates, erase device data, or write evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "RUN_GATE_PREFLIGHT.sh"
EVIDENCE = ROOT / "registry/evidence/v0.12.2/gates"

class PreflightSafetyTests(unittest.TestCase):
    def test_script_never_runs_any_real_gate(self):
        script = PREFLIGHT.read_text(encoding="utf-8")
        self.assertIn("check_real_gate_readiness.py", script)
        for forbidden in ("gate_01_8h_soak.py", "gate_06_android_device.py",
                          "gate_07_ios_iphone_x.py", "RUN_RELEASE_GATE_CLOSURE.sh"):
            self.assertNotIn(forbidden, script)

    def test_run_does_not_change_canonical_evidence(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in EVIDENCE.glob("GATE_*.json")}
        env = dict(os.environ, PYTHON=sys.executable)
        cp = subprocess.run(["bash", str(PREFLIGHT), "--json"], cwd=ROOT,
                            capture_output=True, text=True, timeout=15, env=env)
        self.assertIn(cp.returncode, (0, 2), cp.stderr)
        result = json.loads(cp.stdout)
        self.assertEqual(result["kind"], "READ_ONLY_PREFLIGHT")
        self.assertEqual(len(result["gates"]), 6)
        self.assertEqual([g["gate"][:7] for g in result["gates"]], ["GATE_01", "GATE_02", "GATE_03", "GATE_04", "GATE_06", "GATE_07"])
        for gate in result["gates"]:
            self.assertIn(gate["prerequisites"], ("FOUND", "BLOCKED"))
            self.assertEqual(gate["real_evidence"], "NOT_CHECKED")
            self.assertEqual(gate["user_final_acceptance"], "NOT_PERFORMED")
            self.assertNotEqual(gate["prerequisites"], "PASS")
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in EVIDENCE.glob("GATE_*.json")}
        self.assertEqual(before, after, "Preflight modified release evidence")

    def test_unknown_gate_is_rejected_without_mutation(self):
        cp = subprocess.run(["bash", str(PREFLIGHT), "--gate", "05"],
                            cwd=ROOT, capture_output=True, text=True,
                            timeout=10, env=dict(os.environ, PYTHON=sys.executable))
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("invalid choice", cp.stderr)

if __name__ == "__main__":
    unittest.main()
