from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest

from verification.terminal.harness import REPO_ROOT


EXAMPLE_DIR = REPO_ROOT / "examples/canonical-schema-validation/rust/serde-schemars"
MODELS_RS = EXAMPLE_DIR / "src/models.rs"
README_PATH = EXAMPLE_DIR / "README.md"
SCHEMA_PATH = EXAMPLE_DIR / "workspace_config.schema.json"


class TestSerdeSchemarsCritical(unittest.TestCase):
    def test_schemars_directory_exists(self) -> None:
        self.assertTrue(EXAMPLE_DIR.exists())

    def test_models_rs_has_no_validate_attribute(self) -> None:
        text = MODELS_RS.read_text(encoding="utf-8")
        self.assertNotIn("#[validate", text)
        self.assertNotIn("#[garde", text)
        self.assertIn("JsonSchema", text)

    def test_readme_says_not_a_validator(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("not a validator", text)

    def test_committed_schema_file_exists(self) -> None:
        self.assertTrue(SCHEMA_PATH.exists())
        payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIsInstance(payload, dict)

    def test_schema_has_expected_fields(self) -> None:
        payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        properties = payload.get("properties", {})
        self.assertIn("slug", properties)
        self.assertIn("name", properties)


@unittest.skipIf(shutil.which("cargo") is None, "cargo is not installed")
class TestSerdeSchemarsExecution(unittest.TestCase):
    def test_cargo_run(self) -> None:
        completed = subprocess.run(
            ["cargo", "run"],
            cwd=EXAMPLE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("schema export and drift checks passed", completed.stdout)

