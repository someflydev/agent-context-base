from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import unittest

from verification.terminal.harness import REPO_ROOT


EXAMPLE_DIR = REPO_ROOT / "examples/canonical-schema-validation/rust/validator"
README_PATH = EXAMPLE_DIR / "README.md"


class TestRustValidatorStructure(unittest.TestCase):
    def test_models_rs_exists(self) -> None:
        self.assertTrue((EXAMPLE_DIR / "src/models.rs").exists())

    def test_main_rs_exists(self) -> None:
        self.assertTrue((EXAMPLE_DIR / "src/main.rs").exists())

    def test_readme_mentions_three_library_separation(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("serde", text)
        self.assertIn("schemars", text)
        self.assertIn("validator", text)


@unittest.skipIf(shutil.which("cargo") is None, "cargo is not installed")
class TestRustValidatorExecution(unittest.TestCase):
    def test_cargo_run(self) -> None:
        completed = subprocess.run(
            ["cargo", "run"],
            cwd=EXAMPLE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("valid workspace PASS", completed.stdout)

