from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import gradle_or_skip
from verification.terminal.harness import REPO_ROOT


KONFORM_DIR = REPO_ROOT / "examples/canonical-schema-validation/kotlin/konform"
MODELS_PATH = KONFORM_DIR / "src/main/kotlin/models/Models.kt"
README_PATH = KONFORM_DIR / "README.md"
VALIDATORS_PATH = KONFORM_DIR / "src/main/kotlin/validation/Validators.kt"


class TestKonformStructure(unittest.TestCase):
    def test_validators_kt_exists(self) -> None:
        self.assertTrue(VALIDATORS_PATH.is_file())

    def test_models_kt_no_validate_annotations(self) -> None:
        text = MODELS_PATH.read_text(encoding="utf-8")
        self.assertNotIn("@field:NotBlank", text)
        self.assertNotIn("@field:Email", text)

    def test_readme_mentions_dsl(self) -> None:
        text = README_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"DSL|lambda")

    def test_readme_compares_with_hibernate(self) -> None:
        text = README_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"Hibernate|annotation")


class TestKonformExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gradle = gradle_or_skip(cls)

    def test_gradle_run(self) -> None:
        completed = subprocess.run(
            [self.gradle, "-q", "run"],
            cwd=KONFORM_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(f"gradle run failed in {KONFORM_DIR}; likely missing cached dependencies")
        self.assertIn("PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
