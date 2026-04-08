from __future__ import annotations

import subprocess
from pathlib import Path

from verification.terminal.harness import (
    REPO_ROOT,
    TerminalExample,
    artifact_exists,
    command_exists,
    python_cli_command,
    python_extra_env_for_example,
    python_interpreter_for_example,
    python_modules_available,
)


FIXTURES_DIR = REPO_ROOT / "examples/canonical-terminal/fixtures"
EXAMPLES_ROOT = REPO_ROOT / "examples/canonical-terminal"


def _python_example(name: str, modules: tuple[str, ...]) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    python_executable = python_interpreter_for_example(path)
    return TerminalExample(
        name=name,
        path=path,
        build_cmd=[python_executable, "-m", "pip", "install", "-e", "."],
        smoke_cmd=python_cli_command(
            python_executable,
            "from taskflow.cli.main import main; main()",
            "list",
            "--fixtures-path",
            str(FIXTURES_DIR),
            "--output",
            "json",
        ),
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=lambda path=path, modules=modules: python_modules_available(path, *modules),
        extra_env=python_extra_env_for_example(path),
    )


def _rust_example(name: str) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    debug_binary = path / "target/debug/taskflow"
    release_binary = path / "target/release/taskflow"

    def availability():
        debug_ok, _ = artifact_exists(debug_binary, ["cargo", "build"])
        if debug_ok:
            return True, None
        return artifact_exists(release_binary, ["cargo", "build", "--release"])

    binary = debug_binary if debug_binary.exists() else release_binary
    return TerminalExample(
        name=name,
        path=path,
        build_cmd=["cargo", "build"],
        smoke_cmd=[str(binary), "list", "--output", "json"],
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=availability,
    )


def _go_example(name: str) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    binary = path / "taskflow"
    return TerminalExample(
        name=name,
        path=path,
        build_cmd=["go", "build", "-o", "taskflow", "./..."],
        smoke_cmd=[str(binary), "list", "--output", "json"],
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=lambda binary=binary: artifact_exists(binary, ["go", "build", "-o", "taskflow", "./..."]),
    )


def _node_example(name: str) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    dist_entry = path / "dist/cli/index.js"

    def availability():
        if not command_exists("node"):
            return False, "node is not installed"
        return artifact_exists(dist_entry, ["npm", "run", "build"])

    return TerminalExample(
        name=name,
        path=path,
        build_cmd=["npm", "run", "build"],
        smoke_cmd=["node", str(dist_entry), "list", "--output", "json"],
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=availability,
    )


def _java_example(name: str) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    jar = path / "target/taskflow.jar"

    def availability():
        if not command_exists("java"):
            return False, "java is not installed"
        return artifact_exists(jar, ["mvn", "-q", "package"])

    return TerminalExample(
        name=name,
        path=path,
        build_cmd=["mvn", "-q", "package"],
        smoke_cmd=["java", "-jar", str(jar), "list", "--output", "json"],
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=availability,
    )


def _ruby_example(name: str) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    script = path / "bin/taskflow"

    def availability():
        if not command_exists("ruby"):
            return False, "ruby is not installed"
        artifact_ok, reason = artifact_exists(script, ["bundle", "install"])
        if not artifact_ok:
            return artifact_ok, reason
        if not command_exists("bundle"):
            return False, "bundle is not installed"
        bundle_check = subprocess.run(
            ["bundle", "check"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        if bundle_check.returncode != 0:
            return False, "bundle dependencies are not installed; run bundle install"
        return True, None

    return TerminalExample(
        name=name,
        path=path,
        build_cmd=["bundle", "install"],
        smoke_cmd=["bundle", "exec", "ruby", str(script), "list", "--output", "json"],
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=availability,
    )


def _elixir_example(name: str, escript_name: str) -> TerminalExample:
    path = EXAMPLES_ROOT / name
    escript = path / escript_name

    def availability():
        if not command_exists("mix"):
            return False, "mix is not installed"
        return artifact_exists(escript, ["mix", "escript.build"])

    return TerminalExample(
        name=name,
        path=path,
        build_cmd=["mix", "escript.build"],
        smoke_cmd=[str(escript), "list", "--fixtures-path", str(FIXTURES_DIR), "--output", "json"],
        fixtures_env={"TASKFLOW_FIXTURES_PATH": str(FIXTURES_DIR)},
        expected_marker='"id":',
        availability_check=availability,
    )


TERMINAL_EXAMPLES = [
    _python_example("python-typer-textual", ("typer", "textual")),
    _python_example("python-click-blessed", ("click", "blessed")),
    _rust_example("rust-clap-ratatui"),
    _rust_example("rust-argh-tui-realm"),
    _go_example("go-cobra-bubbletea"),
    _go_example("go-urfave-tview"),
    _node_example("typescript-commander-ink"),
    _node_example("typescript-yargs-blessed"),
    _java_example("java-picocli-lanterna"),
    _java_example("java-jcommander-jline"),
    _ruby_example("ruby-thor-tty"),
    _ruby_example("ruby-clamp-tty"),
    _elixir_example("elixir-optimus-ratatouille", "taskflow"),
    _elixir_example("elixir-optionparser-owl", "taskflow_owl"),
]
