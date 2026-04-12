from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from verification.terminal.harness import REPO_ROOT


EXAMPLE_DIR = REPO_ROOT / "examples/canonical-schema-validation/go/ozzo-validation"
README_PATH = EXAMPLE_DIR / "README.md"


class TestOzzoValidationStructure(unittest.TestCase):
    def test_models_go_exists(self) -> None:
        self.assertTrue((EXAMPLE_DIR / "models/models.go").exists())

    def test_validate_go_exists(self) -> None:
        self.assertTrue((EXAMPLE_DIR / "validate/validate.go").exists())

    def test_readme_mentions_code_driven(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("code", text)

    def test_readme_mentions_cross_field_readability(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertTrue("cross-field" in text or "cross field" in text)


@unittest.skipIf(shutil.which("go") is None, "go is not installed")
class TestOzzoValidationExecution(unittest.TestCase):
    def test_go_test_runs(self) -> None:
        env = dict(os.environ)
        env["GOCACHE"] = str(Path(tempfile.gettempdir()) / "acb-go-cache")
        completed = subprocess.run(
            ["go", "test", "./..."],
            cwd=EXAMPLE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )

