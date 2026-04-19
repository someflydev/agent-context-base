from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTH_ROOT = REPO_ROOT / "examples/canonical-auth"
DOMAIN_ROOT = AUTH_ROOT / "domain"
FIXTURES_ROOT = DOMAIN_ROOT / "fixtures"


class TestDirectoryStructure(unittest.TestCase):
    def test_expected_domain_paths_exist(self) -> None:
        for relative in (
            "examples/canonical-auth",
            "examples/canonical-auth/domain",
            "examples/canonical-auth/CATALOG.md",
            "examples/canonical-auth/domain/spec.md",
            "examples/canonical-auth/domain/parity-matrix.md",
            "examples/canonical-auth/domain/verification-contract.md",
            "examples/canonical-auth/domain/fixtures",
        ):
            with self.subTest(path=relative):
                self.assertTrue((REPO_ROOT / relative).exists(), relative)


class TestSpecContent(unittest.TestCase):
    def setUp(self) -> None:
        self.text = (DOMAIN_ROOT / "spec.md").read_text(encoding="utf-8")

    def test_required_sections_exist(self) -> None:
        for section in (
            "## The Permission Catalog",
            "## JWT Claim Shape Standard",
            "## Canonical Flows",
            "## Route Metadata Specification",
            "## /me Response Shape",
        ):
            with self.subTest(section=section):
                self.assertIn(section, self.text)

    def test_spec_mentions_all_target_languages(self) -> None:
        for language in (
            "Python",
            "TypeScript",
            "Go",
            "Rust",
            "Java",
            "Kotlin",
            "Ruby",
            "Elixir",
        ):
            with self.subTest(language=language):
                self.assertIn(language, self.text)

    def test_permission_catalog_has_at_least_twenty_atoms(self) -> None:
        matches = re.findall(r"`[a-z]+:[a-z_]+:[a-z_]+`", self.text)
        self.assertGreaterEqual(len(set(matches)), 20)

    def test_all_ten_canonical_flows_exist(self) -> None:
        for flow_num in range(1, 11):
            with self.subTest(flow_num=flow_num):
                self.assertIn(f"### Flow {flow_num}:", self.text)

    def test_route_table_has_at_least_twelve_entries(self) -> None:
        route_lines = [
            line
            for line in self.text.splitlines()
            if line.startswith("| ")
            and "/auth/token" not in line
            and "Method" not in line
            and "---" not in line
            and "/" in line
        ]
        self.assertGreaterEqual(len(route_lines), 12)


class TestFixtureFiles(unittest.TestCase):
    def load_array(self, filename: str) -> list[dict[str, object]]:
        path = FIXTURES_ROOT / filename
        self.assertTrue(path.exists(), filename)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        return data

    def test_required_fixture_files_exist_and_are_valid_json(self) -> None:
        for filename in (
            "users.json",
            "tenants.json",
            "groups.json",
            "permissions.json",
            "memberships.json",
        ):
            with self.subTest(filename=filename):
                self.load_array(filename)

    def test_fixture_counts_meet_minimums(self) -> None:
        self.assertGreaterEqual(len(self.load_array("users.json")), 6)
        self.assertGreaterEqual(len(self.load_array("tenants.json")), 2)
        self.assertGreaterEqual(len(self.load_array("groups.json")), 3)
        self.assertGreaterEqual(len(self.load_array("permissions.json")), 10)
        self.assertGreaterEqual(len(self.load_array("memberships.json")), 5)


class TestParityMatrixContent(unittest.TestCase):
    def test_parity_matrix_mentions_all_languages_and_key_columns(self) -> None:
        text = (DOMAIN_ROOT / "parity-matrix.md").read_text(encoding="utf-8")
        for language in (
            "Python",
            "TypeScript",
            "Go",
            "Rust",
            "Java",
            "Kotlin",
            "Ruby",
            "Elixir",
        ):
            with self.subTest(language=language):
                self.assertIn(language, text)
        self.assertIn("Smoke tests passing", text)
        self.assertIn("Cross-tenant denial", text)


class TestCatalogContent(unittest.TestCase):
    def test_catalog_mentions_all_languages_and_parity_matrix(self) -> None:
        text = (AUTH_ROOT / "CATALOG.md").read_text(encoding="utf-8")
        for language in (
            "Python",
            "TypeScript",
            "Go",
            "Rust",
            "Java",
            "Kotlin",
            "Ruby",
            "Elixir",
        ):
            with self.subTest(language=language):
                self.assertIn(language, text)
        self.assertIn("parity-matrix.md", text)


if __name__ == "__main__":
    unittest.main()
