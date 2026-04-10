from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verification.terminal.harness import (
    GOLDEN_DIR,
    REPO_ROOT,
    SmokeResult,
    TerminalExample,
    materialize_fixture_dir,
    python_extra_env_for_example,
    python_interpreter_for_example,
    rewrite_fixtures_path_args,
    run_smoke,
)
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

    def test_materialize_fixture_dir_replaces_requested_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_dir = Path(temp_dir)
            (fixture_dir / "jobs.json").write_text('["base-jobs"]', encoding="utf-8")
            (fixture_dir / "jobs-large.json").write_text('["large-jobs"]', encoding="utf-8")
            (fixture_dir / "events.json").write_text('["base-events"]', encoding="utf-8")
            (fixture_dir / "config.json").write_text('{"queue_name":"taskflow"}', encoding="utf-8")

            with materialize_fixture_dir(fixture_dir, {"jobs.json": "jobs-large.json"}) as active_dir:
                self.assertEqual((active_dir / "jobs.json").read_text(encoding="utf-8"), '["large-jobs"]')
                self.assertEqual((active_dir / "events.json").read_text(encoding="utf-8"), '["base-events"]')
                self.assertEqual((active_dir / "config.json").read_text(encoding="utf-8"), '{"queue_name":"taskflow"}')

    def test_rewrite_fixtures_path_args_updates_cli_flag(self) -> None:
        rewritten = rewrite_fixtures_path_args(
            ["taskflow", "list", "--fixtures-path", "/tmp/base", "--output", "json"],
            Path("/tmp/override"),
        )
        self.assertEqual(
            rewritten,
            ["taskflow", "list", "--fixtures-path", "/tmp/override", "--output", "json"],
        )

    def test_run_smoke_uses_materialized_fixture_dir_for_env_and_command(self) -> None:
        example = TerminalExample(
            name="fixture-test",
            path=REPO_ROOT,
            build_cmd=[],
            smoke_cmd=["taskflow", "list", "--fixtures-path", "/tmp/base", "--output", "json"],
            fixtures_env={"TASKFLOW_FIXTURES_PATH": str(REPO_ROOT / "examples/canonical-terminal/fixtures")},
            expected_marker='"id":',
        )
        completed = type(
            "CompletedProcessLike",
            (),
            {"returncode": 0, "stdout": '{"id":"job-001"}', "stderr": ""},
        )()

        with patch("verification.terminal.harness.subprocess.run", return_value=completed) as run:
            result = run_smoke(example, fixture_overrides={"jobs.json": "jobs.json"})

        self.assertTrue(result.passed)
        command = run.call_args.args[0]
        env = run.call_args.kwargs["env"]
        self.assertEqual(command[2], "--fixtures-path")
        self.assertNotEqual(command[3], "/tmp/base")
        self.assertEqual(env["TASKFLOW_FIXTURES_PATH"], command[3])


if __name__ == "__main__":
    unittest.main()
