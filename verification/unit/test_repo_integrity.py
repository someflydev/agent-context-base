from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, VALID_VERIFICATION_LEVELS, load_registry

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from manifest_tools import normalize_string_list, parse_manifest  # noqa: E402


class RepoIntegrityTests(unittest.TestCase):
    def test_required_directories_exist(self) -> None:
        required = (
            "verification",
            "verification/policies",
            "verification/unit",
            "verification/scripts",
            "verification/examples/python",
            "verification/examples/go",
            "verification/examples/rust",
            "verification/examples/elixir",
            "verification/examples/data",
            "verification/scenarios",
            "verification/fixtures",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).exists(), relative)

    def test_manifest_preferred_examples_exist(self) -> None:
        for manifest_path in sorted((REPO_ROOT / "manifests").glob("*.yaml")):
            data = parse_manifest(manifest_path)
            for ref in normalize_string_list(data.get("preferred_examples")):
                with self.subTest(manifest=manifest_path.name, ref=ref):
                    self.assertTrue((REPO_ROOT / ref).exists(), ref)

    def test_example_registry_paths_and_levels_are_valid(self) -> None:
        entries = load_registry()
        self.assertGreater(len(entries), 10)
        for entry in entries:
            path = str(entry.get("path", ""))
            level = str(entry.get("verification_level", ""))
            with self.subTest(path=path):
                self.assertTrue((REPO_ROOT / path).exists(), path)
                self.assertIn(level, VALID_VERIFICATION_LEVELS)
                if entry.get("scenario_harness"):
                    harness = REPO_ROOT / "verification" / "scenarios" / str(entry["scenario_harness"])
                    self.assertTrue(harness.exists(), harness.as_posix())

    def test_docs_template_references_resolve(self) -> None:
        doc_paths = [
            REPO_ROOT / "README.md",
            *sorted((REPO_ROOT / "docs").glob("*.md")),
            *sorted((REPO_ROOT / "examples").glob("**/*.md")),
            REPO_ROOT / "scripts/README.md",
        ]
        pattern = re.compile(r"(templates/[A-Za-z0-9._/\-]+)")
        for doc_path in doc_paths:
            text = doc_path.read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                template_ref = match.group(1).rstrip(").,")
                with self.subTest(doc=doc_path.name, template_ref=template_ref):
                    self.assertTrue((REPO_ROOT / template_ref).exists(), template_ref)


if __name__ == "__main__":
    unittest.main()
