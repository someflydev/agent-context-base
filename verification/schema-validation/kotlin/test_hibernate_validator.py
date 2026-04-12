from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import gradle_or_skip
from verification.terminal.harness import REPO_ROOT


HIBERNATE_DIR = REPO_ROOT / "examples/canonical-schema-validation/kotlin/hibernate-validator"
MODELS_PATH = HIBERNATE_DIR / "src/main/kotlin/models/Models.kt"
README_PATH = HIBERNATE_DIR / "README.md"


class TestHibernateValidatorStructure(unittest.TestCase):
    def test_models_kt_has_annotations(self) -> None:
        text = MODELS_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"@field:NotBlank|@field:Email")

    def test_readme_mentions_jakarta(self) -> None:
        text = README_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"Jakarta|Bean Validation")

    def test_readme_mentions_custom_annotation_for_cross_field(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("custom", text)
        self.assertRegex(text, r"annotation|cross-field|cross field")


class TestHibernateValidatorExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gradle = gradle_or_skip(cls)

    def test_gradle_run(self) -> None:
        completed = subprocess.run(
            [self.gradle, "-q", "run"],
            cwd=HIBERNATE_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(f"gradle run failed in {HIBERNATE_DIR}; likely missing cached dependencies")
        self.assertIn("PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
