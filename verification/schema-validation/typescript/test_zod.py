from __future__ import annotations

from pathlib import Path
import unittest

from verification.terminal.harness import REPO_ROOT


ZOD_DIR = REPO_ROOT / "examples/canonical-schema-validation/typescript/zod"


class TestZodSmoke(unittest.TestCase):
    def test_zod_directory_exists(self) -> None:
        self.assertTrue(ZOD_DIR.is_dir())

    def test_zod_models_ts_exists(self) -> None:
        self.assertTrue((ZOD_DIR / "src/models.ts").is_file())

    def test_zod_package_json_exists(self) -> None:
        self.assertTrue((ZOD_DIR / "package.json").is_file())

    def test_zod_readme_mentions_lane_c(self) -> None:
        readme = (ZOD_DIR / "README.md").read_text(encoding="utf-8")
        self.assertRegex(readme.lower(), r"lane c|hybrid")


if __name__ == "__main__":
    unittest.main()
