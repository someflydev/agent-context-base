from __future__ import annotations

import unittest

from verification.schema_validation_runtime import run_npm_script
from verification.terminal.harness import REPO_ROOT


IO_TS_DIR = REPO_ROOT / "examples/canonical-schema-validation/typescript/io-ts"


class TestIoTsSmoke(unittest.TestCase):
    def test_io_ts_directory_exists(self) -> None:
        self.assertTrue(IO_TS_DIR.is_dir())

    def test_codecs_ts_exists(self) -> None:
        self.assertTrue((IO_TS_DIR / "src/codecs.ts").is_file())

    def test_readme_mentions_codec_model(self) -> None:
        readme = (IO_TS_DIR / "README.md").read_text(encoding="utf-8")
        self.assertRegex(readme.lower(), r"either|codec")

    def test_readme_distinguishes_from_zod(self) -> None:
        readme = (IO_TS_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("not", readme.lower())
        self.assertRegex(readme, r"Zod|simpler")

    def test_io_ts_runtime_smoke_script(self) -> None:
        completed = run_npm_script(self, IO_TS_DIR, "smoke")
        self.assertIn("io-ts smoke checks passed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
