from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Tuple

from verification.terminal.transcript import assert_transcript


REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = Path(__file__).resolve().parent / "goldens"
AvailabilityCheck = Callable[[], Tuple[bool, Optional[str]]]


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


def run_smoke(
    example: TerminalExample,
    *,
    golden_dir: Optional[Path] = None,
    update_golden: bool = False,
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

    started_at = time.perf_counter()
    try:
        completed = subprocess.run(
            example.smoke_cmd,
            cwd=example.path,
            env=env,
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
) -> dict[str, SmokeResult]:
    if not parallel:
        return {
            example.name: run_smoke(example, golden_dir=golden_dir, update_golden=update_golden)
            for example in examples
        }

    results: dict[str, SmokeResult] = {}
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(examples)))) as executor:
        futures = {
            executor.submit(run_smoke, example, golden_dir=golden_dir, update_golden=update_golden): example.name
            for example in examples
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return results


def python_cli_command(python_executable: str, module_call: str, *argv: str) -> list[str]:
    return [python_executable, "-c", module_call, *argv]
