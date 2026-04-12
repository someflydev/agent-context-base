from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import ruby_or_skip
from verification.terminal.harness import REPO_ROOT


DRY_SCHEMA_DIR = REPO_ROOT / "examples/canonical-schema-validation/ruby/dry-schema"
README_PATH = DRY_SCHEMA_DIR / "README.md"


class TestDrySchemaStructure(unittest.TestCase):
    def test_schema_files_exist(self) -> None:
        self.assertTrue((DRY_SCHEMA_DIR / "schemas/workspace_config_schema.rb").is_file())
        self.assertTrue((DRY_SCHEMA_DIR / "schemas/sync_run_schema.rb").is_file())
        self.assertTrue((DRY_SCHEMA_DIR / "schema_export.rb").is_file())

    def test_readme_mentions_json_schema_export(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("json schema", text)


class TestDrySchemaExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ruby = ruby_or_skip(cls, "json")

    def test_schema_export_runs_when_gems_exist(self) -> None:
        try:
            ruby_or_skip(self, "dry-schema")
        except unittest.SkipTest as exc:
            self.skipTest(str(exc))

        completed = subprocess.run(
            [self.ruby, "schema_export.rb"],
            cwd=DRY_SCHEMA_DIR,
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


if __name__ == "__main__":
    unittest.main()
