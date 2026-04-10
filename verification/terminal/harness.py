from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator, Mapping, Optional, Tuple, Union

from verification.terminal.transcript import assert_transcript


REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = Path(__file__).resolve().parent / "goldens"
AvailabilityCheck = Callable[[], Tuple[bool, Optional[str]]]
FixtureOverrides = Mapping[str, Union[str, Path]]


@dataclass
class TerminalExample:
    name: str
    path: Path
    build_cmd: list[str]
    smoke_cmd: list[str]
    fixtures_env: dict[str, str]
    expected_marker: str
    availability_check: Optional[AvailabilityCheck] = None
    extra_env: dict[str, str] = field(default_factory=dict)


@dataclass
class SmokeResult:
    exit_code: Optional[int]
    stdout: str
    stderr: str
    duration_s: float
    passed: bool
    skipped: bool = False
    skip_reason: Optional[str] = None


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def python_interpreter_for_example(example_path: Path) -> str:
    example_python = example_path / ".venv/bin/python"
    if example_python.exists():
        return str(example_python)
    return sys.executable


def python_extra_env_for_example(example_path: Path) -> dict[str, str]:
    example_python = example_path / ".venv/bin/python"
    if example_python.exists():
        return {}

    pythonpath_parts = [str(example_path)]
    inherited_pythonpath = os.environ.get("PYTHONPATH")
    if inherited_pythonpath:
        pythonpath_parts.append(inherited_pythonpath)
    return {"PYTHONPATH": os.pathsep.join(pythonpath_parts)}


def python_modules_available(example_path: Path, *modules: str) -> Tuple[bool, Optional[str]]:
    command = [
        python_interpreter_for_example(example_path),
        "-c",
        (
            "import importlib.util, sys; "
            "missing = [name for name in sys.argv[1:] if importlib.util.find_spec(name) is None]; "
            "raise SystemExit(0 if not missing else 1)"
        ),
        *modules,
    ]
    completed = subprocess.run(
        command,
        cwd=example_path,
        env={**os.environ, **python_extra_env_for_example(example_path)},
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return True, None
    return False, f"missing Python modules: {', '.join(modules)}"


def artifact_exists(path: Path, build_cmd: list[str]) -> Tuple[bool, Optional[str]]:
    if path.exists():
        return True, None
    if build_cmd:
        return False, f"missing build artifact {path.relative_to(REPO_ROOT)}; run {' '.join(build_cmd)}"
    return False, f"missing required artifact {path.relative_to(REPO_ROOT)}"


@contextlib.contextmanager
def materialize_fixture_dir(
    fixture_dir: Path,
    overrides: Optional[FixtureOverrides] = None,
) -> Iterator[Path]:
    resolved_dir = fixture_dir.expanduser().resolve()
    if not overrides:
        yield resolved_dir
        return

    with tempfile.TemporaryDirectory(prefix="terminal-fixtures-") as temp_dir:
        temp_path = Path(temp_dir)
        for source in resolved_dir.iterdir():
            if source.is_file():
                shutil.copy2(source, temp_path / source.name)

        for canonical_name, override_source in overrides.items():
            source_path = Path(override_source)
            if not source_path.is_absolute():
                source_path = resolved_dir / source_path
            shutil.copy2(source_path.resolve(), temp_path / canonical_name)

        yield temp_path


def rewrite_fixtures_path_args(command: list[str], fixture_dir: Path) -> list[str]:
    rewritten = list(command)
    for index, token in enumerate(rewritten[:-1]):
        if token == "--fixtures-path":
            rewritten[index + 1] = str(fixture_dir)
    return rewritten


def run_smoke(
    example: TerminalExample,
    *,
    golden_dir: Optional[Path] = None,
    update_golden: bool = False,
    fixture_overrides: Optional[FixtureOverrides] = None,
) -> SmokeResult:
    if not example.path.exists():
        return SmokeResult(
            exit_code=None,
            stdout="",
            stderr="",
            duration_s=0.0,
            passed=False,
            skipped=True,
            skip_reason=f"example path does not exist: {example.path}",
        )

    if example.availability_check is not None:
        available, reason = example.availability_check()
        if not available:
            return SmokeResult(
                exit_code=None,
                stdout="",
                stderr="",
                duration_s=0.0,
                passed=False,
                skipped=True,
                skip_reason=reason,
            )

    env = os.environ.copy()
    env.update(example.fixtures_env)
    env.update(example.extra_env)
    fixture_dir = Path(env["TASKFLOW_FIXTURES_PATH"]) if "TASKFLOW_FIXTURES_PATH" in env else None

    with materialize_fixture_dir(fixture_dir, fixture_overrides) if fixture_dir else contextlib.nullcontext(None) as active_fixture_dir:
        if active_fixture_dir is not None:
            env["TASKFLOW_FIXTURES_PATH"] = str(active_fixture_dir)
            command = rewrite_fixtures_path_args(example.smoke_cmd, active_fixture_dir)
        else:
            command = list(example.smoke_cmd)

        started_at = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=example.path,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            duration_s = time.perf_counter() - started_at
        except subprocess.TimeoutExpired as error:
            duration_s = time.perf_counter() - started_at
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            return SmokeResult(
                exit_code=None,
                stdout=stdout,
                stderr=f"{stderr}\nsmoke command timed out after 30 seconds".strip(),
                duration_s=duration_s,
                passed=False,
            )

    passed = completed.returncode == 0 and example.expected_marker in completed.stdout
    stderr = completed.stderr
    if passed and golden_dir is not None:
        passed = assert_transcript(example.name, completed.stdout, golden_dir, update=update_golden)
        if not passed:
            stderr = f"{stderr}\ngolden transcript mismatch".strip()

    return SmokeResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=stderr,
        duration_s=duration_s,
        passed=passed,
    )


def run_all(
    examples: list[TerminalExample],
    parallel: bool = False,
    *,
    golden_dir: Optional[Path] = None,
    update_golden: bool = False,
    fixture_overrides: Optional[FixtureOverrides] = None,
) -> dict[str, SmokeResult]:
    if not parallel:
        return {
            example.name: run_smoke(
                example,
                golden_dir=golden_dir,
                update_golden=update_golden,
                fixture_overrides=fixture_overrides,
            )
            for example in examples
        }

    results: dict[str, SmokeResult] = {}
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(examples)))) as executor:
        futures = {
            executor.submit(
                run_smoke,
                example,
                golden_dir=golden_dir,
                update_golden=update_golden,
                fixture_overrides=fixture_overrides,
            ): example.name
            for example in examples
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return results


def python_cli_command(python_executable: str, module_call: str, *argv: str) -> list[str]:
    return [python_executable, "-c", module_call, *argv]
