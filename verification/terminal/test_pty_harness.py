from __future__ import annotations

import unittest
from pathlib import Path

from verification.terminal.harness import python_extra_env_for_example, python_interpreter_for_example, python_modules_available
from verification.terminal.pty_harness import PEXPECT_AVAILABLE, PtySession, make_watch_script, scripted_tui_test


PYTHON_TEXTUAL_ROOT = (
    Path(__file__).resolve().parents[2]
    / "examples/canonical-terminal/python-typer-textual"
)


class TestPtyHarness(unittest.TestCase):
    @unittest.skipUnless(PEXPECT_AVAILABLE, "requires pexpect")
    def test_pty_harness_importable(self) -> None:
        self.assertTrue(PtySession)

    def test_make_watch_script(self) -> None:
        script = make_watch_script()
        self.assertIsInstance(script, list)
        self.assertEqual(len(script), 3)

    def test_python_textual_tui(self) -> None:
        if not PEXPECT_AVAILABLE:
            self.skipTest("requires pexpect")
        available, reason = python_modules_available(PYTHON_TEXTUAL_ROOT, "textual", "typer")
        if not available:
            self.skipTest(reason or "python-typer-textual runtime is unavailable")

        fixtures = PYTHON_TEXTUAL_ROOT.parent / "fixtures"
        command = [
            python_interpreter_for_example(PYTHON_TEXTUAL_ROOT),
            "-c",
            "from taskflow.cli.main import main; main()",
            "watch",
            "--fixtures-path",
            str(fixtures),
        ]
        env = {
            "TASKFLOW_FIXTURES_PATH": str(fixtures),
            "TERM": "xterm-256color",
        }
        env.update(python_extra_env_for_example(PYTHON_TEXTUAL_ROOT))
        self.assertTrue(scripted_tui_test(command, make_watch_script(), env=env))


if __name__ == "__main__":
    unittest.main()
