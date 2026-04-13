from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
GO_DIR = REPO_ROOT / "examples" / "canonical-faker" / "go"
GO_ENV = {
    **os.environ,
    "GOCACHE": "/tmp/go-build",
    "GOMODCACHE": "/tmp/go-mod-cache",
}


class TestGoFakerExample(unittest.TestCase):
    def test_go_mod_exists(self) -> None:
        go_mod = GO_DIR / "go.mod"
        self.assertTrue(go_mod.exists())
        text = go_mod.read_text(encoding="utf-8")
        self.assertIn("gofakeit", text)
        self.assertIn("go-faker", text)

    def test_types_defined(self) -> None:
        types_go = GO_DIR / "internal" / "domain" / "types.go"
        self.assertTrue(types_go.exists())
        text = types_go.read_text(encoding="utf-8")
        self.assertIn("Organization", text)
        self.assertIn("AuditEvent", text)
        self.assertIn('json:"', text)

    def test_struct_tag_contrast_documented(self) -> None:
        struct_tag = GO_DIR / "internal" / "pipeline" / "struct_tag.go"
        self.assertTrue(struct_tag.exists())
        text = struct_tag.read_text(encoding="utf-8").lower()
        self.assertTrue(
            "relational graph integrity" in text or "orchestration layer" in text
        )

    def test_cli_exists(self) -> None:
        cli = GO_DIR / "cmd" / "generate" / "main.go"
        self.assertTrue(cli.exists())
        text = cli.read_text(encoding="utf-8")
        self.assertIn("flag.String", text)
        self.assertIn("profile", text)

    def test_go_build_if_available(self) -> None:
        if shutil.which("go") is None:
            self.skipTest("go is not installed")
        subprocess.run(["go", "build", "./..."], cwd=GO_DIR, check=True, env=GO_ENV)

    def test_go_smoke_if_available(self) -> None:
        if shutil.which("go") is None:
            self.skipTest("go is not installed")
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["go", "run", "./cmd/generate/", "-profile", "smoke", "-output", tmpdir],
                cwd=GO_DIR,
                check=True,
                env=GO_ENV,
            )
            self.assertTrue((Path(tmpdir) / "smoke" / "organizations.jsonl").exists())
            subprocess.run(
                [
                    "python3",
                    "../domain/validate_output.py",
                    "--input-dir",
                    str(Path(tmpdir) / "smoke"),
                ],
                cwd=GO_DIR,
                check=True,
            )


if __name__ == "__main__":
    unittest.main()
