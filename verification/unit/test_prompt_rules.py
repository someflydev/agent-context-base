from __future__ import annotations

import re
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT


PROMPT_PATTERN = re.compile(r"^PROMPT_(\d{2})(?:_([str]+))?\.txt$")
REFERENCE_PATTERN = re.compile(r"PROMPT_\d{2}(?:_[str]+)?\.txt")


def validate_prompt_tree(root: Path) -> list[str]:
    prompt_dir = root / ".prompts"
    errors: list[str] = []
    prompt_files = [path for path in sorted(prompt_dir.glob("*.txt")) if path.is_file() and not path.name.startswith(".")]
    seen_numbers: dict[int, str] = {}
    executable_numbers: list[int] = []

    for path in prompt_files:
        match = PROMPT_PATTERN.match(path.name)
        if match is None:
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
        if "t" not in suffix:
            executable_numbers.append(number)

        text = path.read_text(encoding="utf-8")
        for ref in REFERENCE_PATTERN.findall(text):
            if not (prompt_dir / ref).exists():
                errors.append(f"{path.name} references missing prompt file {ref}")

    expected = list(range(min(executable_numbers), max(executable_numbers) + 1)) if executable_numbers else []
    if executable_numbers and sorted(executable_numbers) != expected:
        errors.append(
            "prompt numbering must be strictly monotonic for executable prompts"
        )
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


if __name__ == "__main__":
    unittest.main()
