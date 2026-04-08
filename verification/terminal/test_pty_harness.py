from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from verification.terminal.pty_harness import PEXPECT_AVAILABLE, PtySession, make_watch_script, scripted_tui_test


TEXTUAL_INSTALLED = importlib.util.find_spec("textual") is not None
TYPER_INSTALLED = importlib.util.find_spec("typer") is not None


class TestPtyHarness(unittest.TestCase):
    @unittest.skipUnless(PEXPECT_AVAILABLE, "requires pexpect")
    def test_pty_harness_importable(self) -> None:
        self.assertTrue(PtySession)

    def test_make_watch_script(self) -> None:
        script = make_watch_script()
        self.assertIsInstance(script, list)
        self.assertEqual(len(script), 3)

    @unittest.skipUnless(PEXPECT_AVAILABLE and TEXTUAL_INSTALLED and TYPER_INSTALLED, "requires pexpect and textual")
    def test_python_textual_tui(self) -> None:
        root = (
            Path(__file__).resolve().parents[2]
            / "examples/canonical-terminal/python-typer-textual"
        )
        fixtures = root.parent / "fixtures"
        command = [
            sys.executable,
            "-c",
            "from taskflow.cli.main import main; main()",
            "watch",
            "--fixtures-path",
            str(fixtures),
        ]
        env = {
            "PYTHONPATH": str(root),
            "TASKFLOW_FIXTURES_PATH": str(fixtures),
            "TERM": "xterm-256color",
        }
        self.assertTrue(scripted_tui_test(command, make_watch_script(), env=env))


if __name__ == "__main__":
    unittest.main()
