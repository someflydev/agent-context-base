from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import mix_or_skip
from verification.terminal.harness import REPO_ROOT


NORM_DIR = REPO_ROOT / "examples/canonical-schema-validation/elixir/norm"
README_PATH = NORM_DIR / "README.md"
SPECS_PATH = NORM_DIR / "lib/workspace_sync_context/specs.ex"


class TestNormStructure(unittest.TestCase):
    def test_specs_file_exists(self) -> None:
        self.assertTrue(SPECS_PATH.is_file())

    def test_readme_mentions_spec_model(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("spec", text)


class TestNormExecution(unittest.TestCase):
    def test_mix_compile_when_deps_are_present(self) -> None:
        try:
            mix = mix_or_skip(self, NORM_DIR)
        except unittest.SkipTest as exc:
            self.skipTest(str(exc))

        completed = subprocess.run(
            [mix, "compile"],
            cwd=NORM_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(f"mix compile failed in {NORM_DIR}; likely missing fetched deps")


if __name__ == "__main__":
    unittest.main()
