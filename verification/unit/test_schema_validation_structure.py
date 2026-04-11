from __future__ import annotations

import unittest

import yaml

from verification.helpers import REPO_ROOT


class TestSchemaValidationFoundation(unittest.TestCase):
    def test_doctrine_exists(self) -> None:
        path = REPO_ROOT / "context/doctrine/schema-validation-contracts.md"
        self.assertTrue(path.exists())
        self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_doctrine_has_three_lanes(self) -> None:
        text = (
            REPO_ROOT / "context/doctrine/schema-validation-contracts.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Lane A", text)
        self.assertIn("Lane B", text)
        self.assertIn("Lane C", text)

    def test_archetype_exists(self) -> None:
        sibling = REPO_ROOT / "context/archetypes/polyglot-validation-lab.md"
        base = REPO_ROOT / "context/archetypes/polyglot-lab.md"
        self.assertTrue(
            sibling.exists() or "Schema Validation" in base.read_text(encoding="utf-8")
        )

    def test_all_seven_stacks_exist(self) -> None:
        for filename in (
            "schema-validation-python.yaml",
            "schema-validation-typescript.yaml",
            "schema-validation-go.yaml",
            "schema-validation-rust.yaml",
            "schema-validation-kotlin.yaml",
            "schema-validation-ruby.yaml",
            "schema-validation-elixir.yaml",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((REPO_ROOT / "context/stacks" / filename).exists())

    def test_manifest_exists(self) -> None:
        path = REPO_ROOT / "manifests/schema-validation-polyglot.yaml"
        self.assertTrue(path.exists())
        self.assertIsInstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict)

    def test_skills_exist(self) -> None:
        for rel_path in (
            "context/skills/schema-validation-lane-selection.md",
            "context/skills/contract-generation-path-selection.md",
        ):
            with self.subTest(path=rel_path):
                path = REPO_ROOT / rel_path
                self.assertTrue(path.exists())
                self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_workflow_exists(self) -> None:
        path = REPO_ROOT / "context/workflows/add-schema-validation-example.md"
        self.assertTrue(path.exists())
        self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_rust_stack_mentions_schemars(self) -> None:
        text = (
            REPO_ROOT / "context/stacks/schema-validation-rust.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn("schemars", text)
        self.assertIn("contract", text)

    def test_typescript_stack_mentions_io_ts(self) -> None:
        text = (
            REPO_ROOT / "context/stacks/schema-validation-typescript.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn("io-ts", text)

    def test_kotlin_stack_mentions_both_libraries(self) -> None:
        text = (
            REPO_ROOT / "context/stacks/schema-validation-kotlin.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn("Konform", text)
        self.assertIn("Hibernate", text)


if __name__ == "__main__":
    unittest.main()
