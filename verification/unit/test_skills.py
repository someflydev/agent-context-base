from __future__ import annotations

import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT


class TestTerminalSkillsExist(unittest.TestCase):
    def test_terminal_example_selection_exists(self) -> None:
        path = REPO_ROOT / "context/skills/terminal-example-selection.md"
        self.assertTrue(path.exists())
        self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_terminal_validation_path_selection_exists(self) -> None:
        path = REPO_ROOT / "context/skills/terminal-validation-path-selection.md"
        self.assertTrue(path.exists())
        self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_existing_skills_reference_terminal(self) -> None:
        canonical_text = (
            REPO_ROOT / "context/skills/canonical-example-selection.md"
        ).read_text(encoding="utf-8")
        verification_text = (
            REPO_ROOT / "context/skills/verification-path-selection.md"
        ).read_text(encoding="utf-8")
        self.assertIn("terminal", canonical_text)
        self.assertIn("terminal", verification_text)


class TestTerminalSkillContent(unittest.TestCase):
    def test_terminal_example_selection_has_required_sections(self) -> None:
        text = (
            REPO_ROOT / "context/skills/terminal-example-selection.md"
        ).read_text(encoding="utf-8")
        for section in (
            "## Procedure",
            "## Priority",
            "## Good Triggers",
            "## Avoid",
            "## Reference Files",
        ):
            self.assertIn(section, text)

    def test_terminal_validation_path_selection_has_required_sections(self) -> None:
        text = (
            REPO_ROOT / "context/skills/terminal-validation-path-selection.md"
        ).read_text(encoding="utf-8")
        for section in (
            "## Procedure",
            "## Good Triggers",
            "## Avoid",
            "## Reference Files",
        ):
            self.assertIn(section, text)

    def test_terminal_example_selection_names_all_flagships(self) -> None:
        text = (
            REPO_ROOT / "context/skills/terminal-example-selection.md"
        ).read_text(encoding="utf-8")
        for name in (
            "python-typer-textual",
            "rust-clap-ratatui",
            "go-cobra-bubbletea",
            "typescript-commander-ink",
            "java-picocli-lanterna",
            "ruby-thor-tty",
            "elixir-optimus-ratatouille",
        ):
            self.assertIn(name, text)

    def test_terminal_validation_path_references_pty_harness(self) -> None:
        text = (
            REPO_ROOT / "context/skills/terminal-validation-path-selection.md"
        ).read_text(encoding="utf-8")
        self.assertIn("pty_harness", text)

    def test_terminal_validation_path_references_comparison_runner(self) -> None:
        text = (
            REPO_ROOT / "context/skills/terminal-validation-path-selection.md"
        ).read_text(encoding="utf-8")
        self.assertIn("run_terminal_comparison", text)


if __name__ == "__main__":
    unittest.main()
