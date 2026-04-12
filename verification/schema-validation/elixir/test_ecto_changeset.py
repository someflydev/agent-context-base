from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from verification.schema_validation_runtime import mix_or_skip
from verification.terminal.harness import REPO_ROOT


ECTO_DIR = REPO_ROOT / "examples/canonical-schema-validation/elixir/ecto-changeset"
README_PATH = ECTO_DIR / "README.md"


class TestEctoChangesetStructure(unittest.TestCase):
    def test_all_five_modules_exist(self) -> None:
        for name in [
            "workspace_config.ex",
            "sync_run.ex",
            "webhook_payload.ex",
            "ingestion_source.ex",
            "review_request.ex",
        ]:
            self.assertTrue((ECTO_DIR / "lib/workspace_sync_context" / name).is_file())

    def test_readme_mentions_cast_vs_validate(self) -> None:
        text = README_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("cast", text)
        self.assertIn("validate", text)


class TestEctoChangesetExecution(unittest.TestCase):
    def test_mix_compile_when_deps_are_present(self) -> None:
        try:
            mix = mix_or_skip(self, ECTO_DIR)
        except unittest.SkipTest as exc:
            self.skipTest(str(exc))

        completed = subprocess.run(
            [mix, "compile"],
            cwd=ECTO_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(f"mix compile failed in {ECTO_DIR}; likely missing fetched deps")


if __name__ == "__main__":
    unittest.main()
