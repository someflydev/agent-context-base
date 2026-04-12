from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import ruby_or_skip
from verification.terminal.harness import REPO_ROOT


DRY_VALIDATION_DIR = REPO_ROOT / "examples/canonical-schema-validation/ruby/dry-validation"
README_PATH = DRY_VALIDATION_DIR / "README.md"
SYNC_RUN_CONTRACT = DRY_VALIDATION_DIR / "contracts/sync_run_contract.rb"


class TestDryValidationStructure(unittest.TestCase):
    def test_all_five_contracts_exist(self) -> None:
        for name in [
            "workspace_config_contract.rb",
            "sync_run_contract.rb",
            "webhook_payload_contract.rb",
            "ingestion_source_contract.rb",
            "review_request_contract.rb",
        ]:
            self.assertTrue((DRY_VALIDATION_DIR / "contracts" / name).is_file())

    def test_cross_field_rule_in_sync_run_contract(self) -> None:
        text = SYNC_RUN_CONTRACT.read_text(encoding="utf-8")
        self.assertIn("finished_at", text)
        self.assertIn("started_at", text)

    def test_readme_explains_dry_schema_layering(self) -> None:
        text = README_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"dry-schema|params block")


class TestDryValidationExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ruby = ruby_or_skip(cls, "json")

    def test_main_rb_runs_when_gems_exist(self) -> None:
        try:
            ruby_or_skip(self, "dry-validation", "dry/schema")
        except unittest.SkipTest as exc:
            self.skipTest(str(exc))

        completed = subprocess.run(
            [self.ruby, "main.rb"],
            cwd=DRY_VALIDATION_DIR,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("PASS", completed.stdout)
        self.assertIn("FAIL", completed.stdout)


if __name__ == "__main__":
    unittest.main()
