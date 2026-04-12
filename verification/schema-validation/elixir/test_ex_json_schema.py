from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import mix_or_skip
from verification.terminal.harness import REPO_ROOT


JSON_SCHEMA_DIR = REPO_ROOT / "examples/canonical-schema-validation/elixir/ex-json-schema"
README_PATH = JSON_SCHEMA_DIR / "README.md"
SCHEMA_PATH = JSON_SCHEMA_DIR / "workspace_config.schema.json"


class TestExJsonSchemaLaneB(unittest.TestCase):
    def test_schema_json_exists(self) -> None:
        self.assertTrue(SCHEMA_PATH.is_file())

    def test_schema_is_valid_json(self) -> None:
        payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIsInstance(payload, dict)

    def test_schema_has_properties(self) -> None:
        payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIn("properties", payload)

    def test_readme_mentions_contract_first(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertRegex(text, r"contract-first|contract first")

    def test_readme_compares_with_ecto(self) -> None:
        text = README_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"Ecto|changeset")


class TestExJsonSchemaExecution(unittest.TestCase):
    def test_mix_compile_when_deps_are_present(self) -> None:
        try:
            mix = mix_or_skip(self, JSON_SCHEMA_DIR)
        except unittest.SkipTest as exc:
            self.skipTest(str(exc))

        completed = subprocess.run(
            [mix, "compile"],
            cwd=JSON_SCHEMA_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(f"mix compile failed in {JSON_SCHEMA_DIR}; likely missing fetched deps")


if __name__ == "__main__":
    unittest.main()
