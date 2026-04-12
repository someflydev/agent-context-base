from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from verification.terminal.harness import REPO_ROOT


REQUIREMENTS_FILE = REPO_ROOT / "verification/schema-validation/python/requirements.txt"
RUNTIME_VENV = REPO_ROOT / ".venv-schema-validation"


def ensure_node_tooling(test_case: unittest.TestCase, example_dir: Path) -> None:
    if shutil.which("node") is None or shutil.which("npm") is None:
        test_case.skipTest("Node.js/npm are not available in this environment")
    if not (example_dir / "node_modules").is_dir():
        test_case.skipTest(f"local dependencies are not installed in {example_dir}")


def run_npm_script(
    test_case: unittest.TestCase,
    example_dir: Path,
    script: str,
) -> subprocess.CompletedProcess[str]:
    ensure_node_tooling(test_case, example_dir)
    completed = subprocess.run(
        ["npm", "run", script],
        cwd=example_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    test_case.assertEqual(
        completed.returncode,
        0,
        msg=(
            f"`npm run {script}` failed in {example_dir}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        ),
    )
    return completed


def _python_has_modules(python_bin: Path, *modules: str) -> bool:
    completed = subprocess.run(
        [
            str(python_bin),
            "-c",
            (
                "import importlib.util, sys; "
                "missing = [name for name in sys.argv[1:] if importlib.util.find_spec(name) is None]; "
                "raise SystemExit(0 if not missing else 1)"
            ),
            *modules,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def runtime_python_or_skip(
    test_case: unittest.TestCase,
    *modules: str,
) -> Path:
    current_python = Path(sys.executable)
    if _python_has_modules(current_python, *modules):
        return current_python

    venv_python = RUNTIME_VENV / "bin/python"
    if venv_python.exists() and _python_has_modules(venv_python, *modules):
        return venv_python

    if shutil.which("uv") is None:
        test_case.skipTest(
            f"missing Python modules {modules} and uv is unavailable for repo-local runtime setup"
        )

    install_hint = (
        "uv venv .venv-schema-validation && "
        "uv pip install --python .venv-schema-validation/bin/python "
        f"-r {REQUIREMENTS_FILE.relative_to(REPO_ROOT)}"
    )
    test_case.skipTest(
        f"missing Python modules {modules}; install repo-local runtime with: {install_hint}"
    )


def run_python_snippet(
    test_case: unittest.TestCase,
    python_bin: Path,
    code: str,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [str(python_bin), "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    test_case.assertEqual(
        completed.returncode,
        0,
        msg=f"python runtime check failed\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
    )
    return completed
