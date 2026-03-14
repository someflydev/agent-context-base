from __future__ import annotations

import re
import unittest

from verification.helpers import REPO_ROOT, load_yaml_like, registry_by_name


REQUIRED_SECTIONS = (
    "## Capability Gap",
    "## Invariant Layer",
    "## Language Matrix",
    "## Selection Contract",
    "## Verification Posture",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
)


class DataAcquisitionExampleTests(unittest.TestCase):
    def test_readme_contains_all_required_sections(self) -> None:
        path = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, text)
        for pattern in FORBIDDEN_PATTERNS:
            self.assertIsNone(pattern.search(text))

    def test_language_support_matrix_is_complete_and_honest(self) -> None:
        path = REPO_ROOT / "examples/canonical-data-acquisition/language-support-matrix.yaml"
        data = load_yaml_like(path)
        self.assertEqual(data.get("capability"), "canonical-data-acquisition")
        languages = data.get("languages", [])
        self.assertEqual(len(languages), 8)
        registry = registry_by_name()
        for entry in languages:
            with self.subTest(stack=entry.get("stack")):
                self.assertIn(entry.get("stack_specific_examples"), ([], "[]"))
                self.assertEqual(entry.get("verification_posture"), "invariant-layer-only")
                fallback = str(entry.get("fallback_example", ""))
                self.assertIn(fallback, registry)
                self.assertEqual(
                    entry.get("fallback_verification_level"),
                    registry[fallback].get("verification_level"),
                )

    def test_readme_table_rows_match_support_matrix(self) -> None:
        readme = (REPO_ROOT / "examples/canonical-data-acquisition/README.md").read_text(encoding="utf-8")
        data = load_yaml_like(REPO_ROOT / "examples/canonical-data-acquisition/language-support-matrix.yaml")
        for entry in data.get("languages", []):
            row = (
                f"| {entry['language']} | {entry['stack']} | none yet | {entry['verification_posture']} | "
                f"{entry['fallback_path']} ({entry['fallback_verification_level']}) | {entry['follow_on_prompt']} |"
            )
            with self.subTest(stack=entry["stack"]):
                self.assertIn(row, readme)


if __name__ == "__main__":
    unittest.main()
