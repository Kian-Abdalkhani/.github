#!/usr/bin/env python3
"""Exercise validation against temporary candidate trees without editing the repo."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts/validate-templates.py"
BUG_FORM = ".github/ISSUE_TEMPLATE/01-bug-report.yml"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "candidate"
        shutil.copytree(REPOSITORY_ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", ".venv", "node_modules", "__pycache__"))

    def replace(self, name, old, new):
        path = self.root / name
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def run_validation(self):
        return subprocess.run([sys.executable, str(VALIDATOR), "--root", str(self.root)],
                              capture_output=True, text=True, check=False)

    def assert_rejected(self, diagnostic):
        result = self.run_validation()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stderr)

    def test_valid_candidate_preserves_workflow_on(self):
        result = self.run_validation()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_yaml_and_corrected_content(self):
        path = self.root / BUG_FORM
        original = path.read_text()
        path.write_text(original + "broken: [\n")
        self.assert_rejected("invalid YAML")
        path.write_text(original)
        result = self.run_validation()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_yaml_keys(self):
        path = self.root / BUG_FORM
        path.write_text(path.read_text() + "name: Duplicate key\n")
        self.assert_rejected("invalid YAML")

    def test_empty_configuration(self):
        (self.root / ".github/ISSUE_TEMPLATE/config.yml").write_text("")
        self.assert_rejected("YAML document must be a mapping")

    def test_duplicate_response_ids(self):
        self.replace(BUG_FORM, "id: expected-behavior", "id: actual-behavior")
        self.assert_rejected("duplicate field id")

    def test_missing_linked_policy(self):
        (self.root / "SUPPORT.md").unlink()
        self.assert_rejected("missing link target")

    def test_dangling_chooser_destination(self):
        self.replace(".github/ISSUE_TEMPLATE/config.yml", "blob/main/SUPPORT.md",
                     "blob/main/MISSING-POLICY.md")
        self.assert_rejected("missing link target")

    def test_missing_heading_anchor(self):
        self.replace(BUG_FORM, "#suspected-vulnerabilities", "#nonexistent-heading")
        self.assert_rejected("missing heading anchor")

    def test_obsolete_root_paths(self):
        for name in ("ISSUE_TEMPLATE", "workflows"):
            (self.root / name).mkdir()
        (self.root / "dependabot.yml").write_text("version: 2\n")
        result = self.run_validation()
        self.assertEqual(result.returncode, 1)
        for name in ("ISSUE_TEMPLATE", "workflows", "dependabot.yml"):
            self.assertIn(f"{name}: obsolete root path", result.stderr)

    def test_repository_specific_labels(self):
        path = self.root / BUG_FORM
        path.write_text(path.read_text() + "labels: bug\n")
        self.assert_rejected("unsupported shared form metadata")

    def test_non_boolean_required_flag(self):
        self.replace(BUG_FORM, "required: true", 'required: "true"')
        self.assert_rejected("boolean required value")


if __name__ == "__main__":
    unittest.main()
