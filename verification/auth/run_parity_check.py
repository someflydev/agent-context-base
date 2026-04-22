#!/usr/bin/env python3
"""
JWT Auth arc parity check runner.
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
AUTH_DIR = REPO_ROOT / "examples" / "canonical-auth"
FIXTURE_DIR = AUTH_DIR / "domain" / "fixtures"

REQUIRED_IMPLEMENTATIONS = [
    "python",
    "typescript",
    "go",
    "rust",
    "java",
    "kotlin",
    "ruby",
    "elixir",
]

REQUIRED_FIXTURE_FILES = [
    "users.json",
    "tenants.json",
    "groups.json",
    "permissions.json",
    "memberships.json",
]

REQUIRED_FIXTURE_MINIMUMS = {
    "users.json": 6,
    "tenants.json": 2,
    "groups.json": 3,
    "permissions.json": 10,
    "memberships.json": 5,
}

REQUIRED_SPEC_SECTIONS = [
    "## The Permission Catalog",
    "## JWT Claim Shape Standard",
    "## Canonical Flows",
    "## Route Metadata Specification",
    "## /me Response Shape",
    "## Fixture Contract",
]

REQUIRED_README_SECTIONS = [
    "How to run",
    "How to test",
]

DISPLAY_NAMES = {
    "python": "Python",
    "typescript": "TypeScript",
    "go": "Go",
    "rust": "Rust",
    "java": "Java",
    "kotlin": "Kotlin",
    "ruby": "Ruby",
    "elixir": "Elixir",
}


class TestImplementationDirectories(unittest.TestCase):
    def test_all_implementation_dirs_exist(self) -> None:
        for lang in REQUIRED_IMPLEMENTATIONS:
            path = AUTH_DIR / lang
            self.assertTrue(path.exists(), f"Missing implementation directory: {path}")


class TestCatalogCompleteness(unittest.TestCase):
    def test_catalog_exists(self) -> None:
        self.assertTrue((AUTH_DIR / "CATALOG.md").exists())

    def test_all_implementations_present_in_catalog(self) -> None:
        catalog = (AUTH_DIR / "CATALOG.md").read_text()
        for _lang, name in DISPLAY_NAMES.items():
            found_any_status = False
            for line in catalog.splitlines():
                if name in line and any(status in line for status in ("[x]", "[~]", "[ ]")):
                    found_any_status = True
                    break
            self.assertTrue(found_any_status, f"{name} missing from CATALOG.md status table")


class TestParityMatrixCompleteness(unittest.TestCase):
    def test_no_not_started_cells(self) -> None:
        matrix = (AUTH_DIR / "domain" / "parity-matrix.md").read_text()
        not_started = [
            line for line in matrix.splitlines() if "| [ ]" in line or "|[ ]" in line
        ]
        self.assertEqual(
            not_started,
            [],
            "Parity matrix has incomplete rows:\n" + "\n".join(not_started),
        )

    def test_no_partial_rows_when_claiming_completion(self) -> None:
        matrix = (AUTH_DIR / "domain" / "parity-matrix.md").read_text()
        partial_rows = [
            line for line in matrix.splitlines() if "| [~]" in line or "|[~]" in line
        ]
        self.assertEqual(
            partial_rows,
            [],
            "Parity matrix still has partial rows. Resolve the remaining "
            "environment-dependent verification work and support artifacts "
            "before claiming arc completion:\n"
            + "\n".join(partial_rows),
        )


class TestFixtureFiles(unittest.TestCase):
    def test_fixture_files_exist_and_valid(self) -> None:
        for filename in REQUIRED_FIXTURE_FILES:
            path = FIXTURE_DIR / filename
            self.assertTrue(path.exists(), f"Missing fixture: {path}")
            data = json.loads(path.read_text())
            self.assertIsInstance(data, list, f"{filename} should be a JSON array")
            minimum = REQUIRED_FIXTURE_MINIMUMS.get(filename, 1)
            self.assertGreaterEqual(
                len(data),
                minimum,
                f"{filename}: expected >= {minimum} entries, got {len(data)}",
            )


class TestDomainSpecSections(unittest.TestCase):
    def test_spec_has_required_sections(self) -> None:
        spec = (AUTH_DIR / "domain" / "spec.md").read_text()
        for section in REQUIRED_SPEC_SECTIONS:
            self.assertIn(section, spec, f"Missing section in spec.md: {section}")


class TestReadmeFiles(unittest.TestCase):
    def test_all_readmes_exist_with_required_sections(self) -> None:
        for lang in REQUIRED_IMPLEMENTATIONS:
            readme = AUTH_DIR / lang / "README.md"
            self.assertTrue(readme.exists(), f"Missing README: {readme}")
            text = readme.read_text()
            for section in REQUIRED_README_SECTIONS:
                self.assertIn(
                    section,
                    text,
                    f"README for {lang} missing section: '{section}'",
                )


class TestArcDocumentation(unittest.TestCase):
    def test_arc_overview_exists(self) -> None:
        path = REPO_ROOT / "docs" / "jwt-auth-arc-overview.md"
        self.assertTrue(path.exists(), "Missing docs/jwt-auth-arc-overview.md")

    def test_arc_overview_has_implementation_matrix(self) -> None:
        text = (REPO_ROOT / "docs" / "jwt-auth-arc-overview.md").read_text()
        self.assertIn("Implementation Matrix", text)

    def test_arc_overview_has_all_eight_languages(self) -> None:
        text = (REPO_ROOT / "docs" / "jwt-auth-arc-overview.md").read_text()
        for language in DISPLAY_NAMES.values():
            self.assertIn(language, text, f"Arc overview missing language: {language}")


if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=2)
    sys.exit(0 if result.result.wasSuccessful() else 1)
