from __future__ import annotations

import re
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, load_yaml_like, registry_by_name, verification_score


REQUIRED_SECTIONS = (
    "## Capability Gap",
    "## Coverage Overview",
    "## Invariant Layer",
    "## Language Matrix",
    "## Shared Semantic Contract",
    "## Selection Contract",
    "## Verification Posture",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
)


def render_stack_specific_cell(entry: dict[str, object], registry: dict[str, dict[str, object]]) -> str:
    names = entry.get("stack_specific_examples", [])
    if not isinstance(names, list) or not names:
        return "none yet"

    items: list[str] = []
    for name in names:
        registry_entry = registry[str(name)]
        items.append(
            f"{Path(str(registry_entry['path'])).name} ({registry_entry['verification_level']})"
        )
    return ", ".join(items)


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
        self.assertEqual(len(languages), 14)
        registry = registry_by_name()
        for entry in languages:
            with self.subTest(stack=entry.get("stack")):
                stack_specific_examples = entry.get("stack_specific_examples", [])
                self.assertIsInstance(stack_specific_examples, list)
                self.assertTrue(str(entry.get("coverage_note", "")).strip())
                fallback = str(entry.get("fallback_example", ""))
                self.assertIn(fallback, registry)
                self.assertEqual(
                    entry.get("fallback_verification_level"),
                    registry[fallback].get("verification_level"),
                )
                if stack_specific_examples:
                    levels = [
                        str(registry[str(name)]["verification_level"])
                        for name in stack_specific_examples
                    ]
                    strongest = max(levels, key=lambda level: verification_score({"verification_level": level}))
                    self.assertEqual(entry.get("verification_posture"), strongest)
                    for name in stack_specific_examples:
                        self.assertIn(str(name), registry)
                else:
                    self.assertEqual(entry.get("verification_posture"), "invariant-layer-only")

    def test_readme_table_rows_match_support_matrix(self) -> None:
        readme = (REPO_ROOT / "examples/canonical-data-acquisition/README.md").read_text(encoding="utf-8")
        data = load_yaml_like(REPO_ROOT / "examples/canonical-data-acquisition/language-support-matrix.yaml")
        registry = registry_by_name()
        for entry in data.get("languages", []):
            row = (
                f"| {entry['language']} | {entry['stack']} | "
                f"{render_stack_specific_cell(entry, registry)} | {entry['verification_posture']} | "
                f"{entry['fallback_path']} ({entry['fallback_verification_level']}) | {entry['follow_on_prompt']} |"
            )
            with self.subTest(stack=entry["stack"]):
                self.assertIn(row, readme)

    def test_readme_references_real_stack_specific_examples(self) -> None:
        readme = (REPO_ROOT / "examples/canonical-data-acquisition/README.md").read_text(encoding="utf-8")
        registry = registry_by_name()
        for name in (
            "fastapi-source-sync-example",
            "go-echo-source-sync-example",
            "clojure-kit-source-sync-example",
            "scala-tapir-source-sync-example",
            "kotlin-http4k-source-sync-example",
            "phoenix-source-sync-example",
            "rust-axum-source-sync-example",
            "typescript-hono-source-sync-example",
            "nim-jester-source-sync-example",
            "zig-zap-source-sync-example",
            "crystal-kemal-source-sync-example",
        ):
            with self.subTest(name=name):
                path = Path(str(registry[name]["path"]))
                self.assertIn(path.name, readme)
                self.assertTrue((REPO_ROOT / path).exists())


if __name__ == "__main__":
    unittest.main()
