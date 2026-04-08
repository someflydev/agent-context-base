from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verification.terminal.harness import GOLDEN_DIR, REPO_ROOT, SmokeResult, python_extra_env_for_example, python_interpreter_for_example
from verification.terminal.registry import TERMINAL_EXAMPLES
from verification.terminal.runner import main as runner_main


class TestTerminalHarness(unittest.TestCase):
    def test_registry_has_all_14_examples(self) -> None:
        self.assertEqual(len(TERMINAL_EXAMPLES), 14)
        for example in TERMINAL_EXAMPLES:
            with self.subTest(example=example.name):
                self.assertTrue(example.name)
                self.assertTrue(example.path)
                self.assertTrue(example.smoke_cmd)
                self.assertTrue(example.expected_marker)

    def test_registry_paths_exist(self) -> None:
        for example in TERMINAL_EXAMPLES:
            with self.subTest(example=example.name):
                self.assertTrue(example.path.exists(), example.path)

    def test_fixture_path_exists(self) -> None:
        fixture_path = REPO_ROOT / "examples/canonical-terminal/fixtures/jobs.json"
        self.assertTrue(fixture_path.exists(), fixture_path)

    def test_python_runtime_prefers_example_venv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            example_path = Path(temp_dir)
            venv_python = example_path / ".venv/bin/python"
            venv_python.parent.mkdir(parents=True)
            venv_python.write_text("", encoding="utf-8")

            self.assertEqual(python_interpreter_for_example(example_path), str(venv_python))
            self.assertEqual(python_extra_env_for_example(example_path), {})

    def test_python_runtime_falls_back_to_current_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            example_path = Path(temp_dir)

            self.assertEqual(python_interpreter_for_example(example_path), sys.executable)
            self.assertEqual(
                python_extra_env_for_example(example_path),
                {"PYTHONPATH": str(example_path)},
            )

    def test_python_examples_use_selected_runtime(self) -> None:
        python_examples = [example for example in TERMINAL_EXAMPLES if example.name.startswith("python-")]
        self.assertEqual(len(python_examples), 2)
        for example in python_examples:
            with self.subTest(example=example.name):
                expected_python = python_interpreter_for_example(example.path)
                self.assertEqual(example.build_cmd[0], expected_python)
                self.assertEqual(example.smoke_cmd[0], expected_python)
                self.assertEqual(example.extra_env, python_extra_env_for_example(example.path))

    def test_ruby_examples_run_under_bundle_exec(self) -> None:
        ruby_examples = [example for example in TERMINAL_EXAMPLES if example.name.startswith("ruby-")]
        self.assertEqual(len(ruby_examples), 2)
        for example in ruby_examples:
            with self.subTest(example=example.name):
                self.assertEqual(example.smoke_cmd[:3], ["bundle", "exec", "ruby"])

    def test_runner_passes_golden_dir_without_update_flag(self) -> None:
        result = SmokeResult(
            exit_code=0,
            stdout='{"id":"job-001"}',
            stderr="",
            duration_s=0.1,
            passed=True,
        )
        with patch("verification.terminal.runner.run_all", return_value={"python-typer-textual": result}) as run_all:
            exit_code = runner_main(["--example", "python-typer-textual"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(run_all.call_args.kwargs["golden_dir"], GOLDEN_DIR)
        self.assertFalse(run_all.call_args.kwargs["update_golden"])


if __name__ == "__main__":
    unittest.main()
