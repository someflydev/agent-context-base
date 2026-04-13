from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RUST_DIR = REPO_ROOT / "examples" / "canonical-faker" / "rust"
RUST_ENV = {**os.environ, "CARGO_HOME": "/tmp/prompt123-cargo-home"}


class TestRustFakerExample(unittest.TestCase):
    def test_cargo_toml_exists(self) -> None:
        path = RUST_DIR / "Cargo.toml"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("fake", text)
        self.assertIn("rand", text)

    def test_domain_types_defined(self) -> None:
        path = RUST_DIR / "src" / "domain.rs"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("Organization", text)
        self.assertIn("AuditEvent", text)

    def test_pipeline_uses_builder_pattern(self) -> None:
        path = RUST_DIR / "src" / "pipeline.rs"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("PipelineBuilder", text)

    def test_smoke_tests_exist(self) -> None:
        path = RUST_DIR / "tests" / "smoke_test.rs"
        self.assertTrue(path.exists())
        self.assertIn("#[test]", path.read_text(encoding="utf-8"))

    def test_rust_build_if_available(self) -> None:
        if shutil.which("cargo") is None:
            self.skipTest("cargo is not installed")
        try:
            subprocess.run(
                ["cargo", "build", "--manifest-path", str(RUST_DIR / "Cargo.toml")],
                check=True,
                cwd=RUST_DIR,
                env=RUST_ENV,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            text = (exc.stdout or "") + (exc.stderr or "")
            if "Could not resolve host" in text or "failed to download" in text:
                self.skipTest("cargo dependencies are not reachable in the current sandbox")
            raise

    def test_rust_smoke_if_available(self) -> None:
        if shutil.which("cargo") is None:
            self.skipTest("cargo is not installed")
        try:
            subprocess.run(
                ["cargo", "test", "--test", "smoke_test"],
                check=True,
                cwd=RUST_DIR,
                env=RUST_ENV,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            text = (exc.stdout or "") + (exc.stderr or "")
            if "Could not resolve host" in text or "failed to download" in text:
                self.skipTest("cargo dependencies are not reachable in the current sandbox")
            raise
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                [
                    "cargo",
                    "run",
                    "--",
                    "--profile",
                    "smoke",
                    "--output",
                    tmpdir,
                ],
                check=True,
                cwd=RUST_DIR,
                env=RUST_ENV,
            )
            subprocess.run(
                [
                    "python3",
                    "../domain/validate_output.py",
                    "--input-dir",
                    str(Path(tmpdir) / "smoke"),
                ],
                check=True,
                cwd=RUST_DIR,
            )


if __name__ == "__main__":
    unittest.main()
