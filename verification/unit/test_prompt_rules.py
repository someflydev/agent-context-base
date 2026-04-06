from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT


PROMPT_PATTERN = re.compile(r"^PROMPT_(\d+)(?:_([str]+))?\.txt$")
REFERENCE_PATTERN = re.compile(r"PROMPT_\d+(?:_[str]+)?\.txt")
# The base repo intentionally keeps a few authoring and operator helper prompts
# outside the generated-repo PROMPT_XX sequence. Generated repos should normally
# only add initial-prompt.txt outside that sequence.
ALLOWED_NON_SEQUENTIAL_PROMPT_FILES = {
    "initial-prompt.txt",
    "PROMPT_META_RUNNER.txt",
    "improvements-before-initial-run.txt",
}


def validate_prompt_tree(root: Path) -> list[str]:
    prompt_dir = root / ".prompts"
    errors: list[str] = []
    prompt_files = [
        path
        for path in sorted(prompt_dir.glob("*.txt"))
        if path.is_file() and not path.name.startswith(".")
    ]
    seen_numbers: dict[int, str] = {}
    executable_numbers: list[int] = []
    template_numbers: set[int] = set()

    for path in prompt_files:
        match = PROMPT_PATTERN.match(path.name)
        if match is None:
            if path.name not in ALLOWED_NON_SEQUENTIAL_PROMPT_FILES:
                errors.append(
                    "only initial-prompt.txt may exist outside the PROMPT_XX.txt sequence"
                )
            for ref in REFERENCE_PATTERN.findall(path.read_text(encoding="utf-8")):
                if not (prompt_dir / ref).exists():
                    errors.append(f"{path.name} references missing prompt file {ref}")
            continue

        number = int(match.group(1))
        suffix = match.group(2) or ""
        prior = seen_numbers.get(number)
        if prior is not None:
            errors.append(f"duplicate prompt number {number:02d}: {prior} and {path.name}")
        seen_numbers[number] = path.name

        if "s" in suffix and number != 0:
            errors.append(f"system suffix reserved for prompt 00: {path.name}")
        if "t" in suffix and "s" in suffix:
            errors.append(f"template prompts must not also be system prompts: {path.name}")
        if "t" in suffix:
            template_numbers.add(number)
        else:
            executable_numbers.append(number)

        text = path.read_text(encoding="utf-8")
        for ref in REFERENCE_PATTERN.findall(text):
            if not (prompt_dir / ref).exists():
                errors.append(f"{path.name} references missing prompt file {ref}")

    if executable_numbers:
        expected = list(range(min(executable_numbers), max(executable_numbers) + 1))
        covered_numbers = sorted(set(executable_numbers) | template_numbers)
        if covered_numbers != expected:
            errors.append("prompt numbering must be strictly monotonic for executable prompts")
    return errors


class PromptRuleTests(unittest.TestCase):
    def test_live_prompt_tree_passes(self) -> None:
        errors = validate_prompt_tree(REPO_ROOT)
        self.assertEqual(errors, [])

    def test_broken_fixture_fails(self) -> None:
        fixture_root = REPO_ROOT / "verification/fixtures/broken_prompt_sequence"
        errors = validate_prompt_tree(fixture_root)
        self.assertTrue(errors)
        self.assertTrue(any("duplicate prompt number" in error for error in errors))
        self.assertTrue(any("references missing prompt file" in error for error in errors))

    def test_initial_prompt_is_the_only_allowed_non_sequence_prompt_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_dir = root / ".prompts"
            prompt_dir.mkdir()
            (prompt_dir / "PROMPT_01.txt").write_text("first\n", encoding="utf-8")
            (prompt_dir / "initial-prompt.txt").write_text("operator brief\n", encoding="utf-8")
            self.assertEqual(validate_prompt_tree(root), [])

            (prompt_dir / "notes.txt").write_text("not allowed\n", encoding="utf-8")
            errors = validate_prompt_tree(root)
            self.assertTrue(
                any("only initial-prompt.txt may exist outside the PROMPT_XX.txt sequence" in error for error in errors)
            )


if __name__ == "__main__":
    unittest.main()
