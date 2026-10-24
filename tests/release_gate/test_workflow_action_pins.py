#!/usr/bin/env python3
"""Regression: workflow action refs must be pinned to immutable commit SHAs."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "release_gate" / "consolidate_release_state.py"
spec = importlib.util.spec_from_file_location("naqya_release_state", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def check_workflow(source, filename="quality.yml"):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        workflows = root / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / filename).write_text(source, encoding="utf-8")
        errors = []
        with patch.object(module, "ROOT", root):
            module.validate_workflow_pins(errors)
        return errors


class WorkflowActionPinTests(unittest.TestCase):
    def test_floating_ref_with_indented_uses_is_rejected(self):
        errors = check_workflow("    uses: actions/checkout@v4\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("actions/checkout@v4", errors[0])

    def test_floating_ref_with_list_dash_is_rejected(self):
        errors = check_workflow("    - uses: actions/setup-python@v5\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("actions/setup-python@v5", errors[0])

    def test_quoted_floating_ref_is_rejected(self):
        for quote in ("'", '"'):
            with self.subTest(quote=quote):
                errors = check_workflow(
                    f"    uses: {quote}actions/checkout@v4{quote}\n"
                )
                self.assertEqual(len(errors), 1)

    def test_pinned_ref_and_local_action_are_allowed(self):
        sha = "11d5960a326750d5838078e36cf38b85af677262"
        source = (
            f"    uses: actions/checkout@{sha} # v4\n"
            "    - uses: ./local-action\n"
        )
        self.assertEqual(check_workflow(source), [])

    def test_yaml_suffix_is_checked(self):
        errors = check_workflow("    uses: actions/checkout@v4\n", filename="deploy.yaml")
        self.assertEqual(len(errors), 1)
        self.assertIn("deploy.yaml:1", errors[0])

    def test_missing_and_dynamic_refs_fail_closed(self):
        for value in ("actions/checkout", "docker://alpine:3.18", "''",
                      "actions/checkout@${{ github.ref }}"):
            with self.subTest(value=value):
                errors = check_workflow(f"    uses: {value}\n")
                self.assertEqual(len(errors), 1)

    def test_quoted_local_action_with_comment_is_allowed(self):
        self.assertEqual(
            check_workflow('    uses: "./.github/actions/local" # local\n'), []
        )

    def test_comment_is_not_mistaken_for_action(self):
        self.assertEqual(
            check_workflow("    # uses: actions/checkout@v4\n"), []
        )


if __name__ == "__main__":
    unittest.main()
