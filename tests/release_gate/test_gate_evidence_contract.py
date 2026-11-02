"""Regressionen für die kanonische Release-Evidence-Auswertung.

Alle Daten in diesem Test sind synthetische Fixtures, KEINE reale Gate-Evidence.
"""
from __future__ import annotations

import errno

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

    @staticmethod
    def valid_storage_fields():
        return {
            "tests": {
                "dev_full": {"status": "PASS", "errno": errno.ENOSPC},
                "read_only_mount": {"status": "PASS", "errno": errno.EROFS},
            },
            "application_failure_matrix_evidence_present": True,
            "application_failure_matrix_pass": True,
        }

    def test_storage_pass_without_kernel_probes_is_invalid(self):
        self.write_gate("05", "STORAGE_FAILURE", "PASS")
        self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "INVALID_EVIDENCE")

    def test_storage_pass_rejects_wrong_errno_and_bool_errno(self):
        for bad_errno in (errno.EACCES, True):
            fields = self.valid_storage_fields()
            fields["tests"]["dev_full"]["errno"] = bad_errno
            self.write_gate("05", "STORAGE_FAILURE", "PASS", **fields)
            self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "INVALID_EVIDENCE")

    def test_storage_pass_requires_application_recovery_matrix(self):
        fields = self.valid_storage_fields()
        fields["application_failure_matrix_pass"] = False
        self.write_gate("05", "STORAGE_FAILURE", "PASS", **fields)
        self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "INVALID_EVIDENCE")

    def test_storage_pass_with_full_structure_is_accepted(self):
        self.write_gate("05", "STORAGE_FAILURE", "PASS", **self.valid_storage_fields())
        self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "PASS")


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

    def microphone_metadata(self):
        return {
            "physical_capture_seconds": 2.0,
            "bytes": 1024,
            "sha256": "a" * 64,
            "asset_id": "synthetic-asset-01",
        }

    def test_microphone_bare_pass_is_invalid(self):
        self.write_gate("04", "LINUX_MICROPHONE", "PASS")
        self.assertEqual(read_gate(self.root, "04", "LINUX_MICROPHONE")["status"], "INVALID_EVIDENCE")

    def test_microphone_zero_bytes_is_invalid(self):
        self.write_gate("04", "LINUX_MICROPHONE", "PASS", **(self.microphone_metadata() | {"bytes": 0}))
        self.assertEqual(read_gate(self.root, "04", "LINUX_MICROPHONE")["status"], "INVALID_EVIDENCE")

    def test_microphone_invalid_digest_is_invalid(self):
        self.write_gate("04", "LINUX_MICROPHONE", "PASS", **(self.microphone_metadata() | {"sha256": "bad"}))
        self.assertEqual(read_gate(self.root, "04", "LINUX_MICROPHONE")["status"], "INVALID_EVIDENCE")

    def test_microphone_nonfinite_duration_is_invalid(self):
        self.write_gate("04", "LINUX_MICROPHONE", "PASS", **(self.microphone_metadata() | {"physical_capture_seconds": float("nan")}))
        self.assertEqual(read_gate(self.root, "04", "LINUX_MICROPHONE")["status"], "INVALID_EVIDENCE")

    def test_microphone_capture_metadata_is_structurally_accepted(self):
        self.write_gate("04", "LINUX_MICROPHONE", "PASS", **self.microphone_metadata())
        self.assertEqual(read_gate(self.root, "04", "LINUX_MICROPHONE")["status"], "PASS")

    def test_microphone_blocked_status_remains_blocked(self):
        self.write_gate("04", "LINUX_MICROPHONE", "BLOCKED")
        self.assertEqual(read_gate(self.root, "04", "LINUX_MICROPHONE")["status"], "BLOCKED")


    def test_malformed_and_non_object_json_are_invalid(self):
        path = self.gates / "GATE_03_FIREFOX.json"
        path.write_text("{invalid")
        self.assertEqual(read_gate(self.root, "03", "FIREFOX")["status"], "INVALID_EVIDENCE")
        path.write_text('["PASS"]')
        self.assertEqual(read_gate(self.root, "03", "FIREFOX")["status"], "INVALID_EVIDENCE")

    def test_non_string_status_is_invalid_not_exception(self):
        self.write_gate("03", "FIREFOX", ["PASS"])
        self.assertEqual(read_gate(self.root, "03", "FIREFOX")["status"], "INVALID_EVIDENCE")

    def test_non_finite_soak_duration_is_invalid(self):
        self.write_gate(
            "01", "8H_SOAK", "PASS", qualification="FULL_8H",
            required_seconds=28800, executed_seconds=float("inf"), integrity="ok", errors=[]
        )
        self.assertEqual(read_gate(self.root, "01", "8H_SOAK")["status"], "INVALID_EVIDENCE")

    def test_symlink_evidence_is_invalid(self):
        target = self.root / "outside.json"
        target.write_text('{"gate":"GATE_05_STORAGE_FAILURE","status":"PASS"}')
        (self.gates / "GATE_05_STORAGE_FAILURE.json").symlink_to(target)
        self.assertEqual(read_gate(self.root, "05", "STORAGE_FAILURE")["status"], "INVALID_EVIDENCE")

    @staticmethod
    def complete_android_evidence():
        # Synthetische Felder aus gate_06_android_device.py; kein echtes Geraet.
        return {
            "adb": "/usr/bin/adb",
            "acceptance_apk": "/tmp/acceptance.apk",
            "release_apk": "/tmp/release.apk",
            "package": "de.provoware.naqya",
            "runtime_source": "V0.12.2",
            "devices": ["device-123"],
            "serial": "device-123",
            "model": "Pixel",
            "sdk": "34",
            "reminder_fired": True,
            "run_result": {"mode": "run", "status": "PASS"},
            "verify_result": {"mode": "verify", "status": "PASS"},
            "release_version_name": "0.12.2",
            "release_pid": "1234",
        }

    def test_android_bare_pass_is_invalid(self):
        self.write_gate("06", "ANDROID_DEVICE", "PASS")
        self.assertEqual(
            read_gate(self.root, "06", "ANDROID_DEVICE")["status"],
            "INVALID_EVIDENCE",
        )

    def test_android_complete_pass_structure_is_accepted(self):
        self.write_gate("06", "ANDROID_DEVICE", "PASS", **self.complete_android_evidence())
        self.assertEqual(read_gate(self.root, "06", "ANDROID_DEVICE")["status"], "PASS")

    def test_android_partial_and_inconsistent_pass_is_invalid(self):
        full = self.complete_android_evidence()
        for missing in (
            "adb", "acceptance_apk", "release_apk", "serial", "model",
            "sdk", "release_pid", "devices", "reminder_fired",
            "run_result", "verify_result", "release_version_name",
        ):
            with self.subTest(missing=missing):
                partial = dict(full)
                partial.pop(missing)
                self.write_gate("06", "ANDROID_DEVICE", "PASS", **partial)
                self.assertEqual(read_gate(self.root, "06", "ANDROID_DEVICE")["status"], "INVALID_EVIDENCE")
        for field, value in (
            ("devices", ["different-device"]),
            ("run_result", {"mode": "verify", "status": "PASS"}),
            ("verify_result", {"mode": "run", "status": "PASS"}),
            ("reminder_fired", 1),
            ("release_pid", " "),
        ):
            with self.subTest(field=field):
                partial = dict(full)
                partial[field] = value
                self.write_gate("06", "ANDROID_DEVICE", "PASS", **partial)
                self.assertEqual(read_gate(self.root, "06", "ANDROID_DEVICE")["status"], "INVALID_EVIDENCE")

    def test_android_blocked_does_not_require_pass_fields(self):
        self.write_gate("06", "ANDROID_DEVICE", "BLOCKED")
        self.assertEqual(read_gate(self.root, "06", "ANDROID_DEVICE")["status"], "BLOCKED")


    def test_symlinked_gate_parent_is_invalid(self):
        self.write_gate("03", "FIREFOX", "PASS")
        outside = self.root / "outside-gates"
        self.gates.rename(outside)
        self.gates.symlink_to(outside, target_is_directory=True)
        self.assertEqual(
            read_gate(self.root, "03", "FIREFOX")["status"], "INVALID_EVIDENCE"
        )

    def test_symlinked_mobile_source_parent_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence = root / "registry/evidence"
            evidence.mkdir(parents=True)
            outside = root / "outside-source"
            outside.mkdir()
            (outside / "MOBILE_RUNTIME_SOURCE_ACCEPTANCE.json").write_text(
                '{"status":"PASS"}'
            )
            (evidence / "v0.12.2").symlink_to(outside, target_is_directory=True)
            self.assertEqual(mobile_source_status(root), "INVALID_EVIDENCE")


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
        self.write_gate("05", "STORAGE_FAILURE", "PASS", **self.valid_storage_fields())
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
