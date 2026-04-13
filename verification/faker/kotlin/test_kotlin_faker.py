from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
KOTLIN_DIR = REPO_ROOT / "examples" / "canonical-faker" / "kotlin"


class TestKotlinFakerExample(unittest.TestCase):
    def _gradle_available(self) -> bool:
        if shutil.which("gradle") is None:
            return False
        probe = subprocess.run(["gradle", "-version"], capture_output=True, text=True, check=False)
        return probe.returncode == 0

    def test_build_gradle_exists(self) -> None:
        path = KOTLIN_DIR / "build.gradle.kts"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").lower()
        self.assertIn("kotlin-faker", text)
        self.assertIn("datafaker", text)

    def test_entities_defined(self) -> None:
        path = KOTLIN_DIR / "src" / "main" / "kotlin" / "io" / "agentcontextbase" / "faker" / "domain" / "Entities.kt"
        self.assertTrue(path.exists())
        self.assertIn("data class Organization", path.read_text(encoding="utf-8"))

    def test_two_pipelines_exist(self) -> None:
        kotlin_path = KOTLIN_DIR / "src" / "main" / "kotlin" / "io" / "agentcontextbase" / "faker" / "pipeline" / "KotlinFakerPipeline.kt"
        datafaker_path = KOTLIN_DIR / "src" / "main" / "kotlin" / "io" / "agentcontextbase" / "faker" / "pipeline" / "DatafakerPipeline.kt"
        self.assertTrue(kotlin_path.exists())
        self.assertTrue(datafaker_path.exists())
        text = datafaker_path.read_text(encoding="utf-8")
        self.assertTrue("kotlin-faker" in text or "DSL" in text or "idiomatic" in text)

    def test_gradle_build_if_available(self) -> None:
        if not self._gradle_available():
            self.skipTest("gradle or a usable Java runtime is not installed")
        subprocess.run(["gradle", "build", "--project-dir", str(KOTLIN_DIR)], check=True, cwd=KOTLIN_DIR)

    def test_kotlin_smoke_if_available(self) -> None:
        if not self._gradle_available():
            self.skipTest("gradle or a usable Java runtime is not installed")
        subprocess.run(["gradle", "test", "--project-dir", str(KOTLIN_DIR)], check=True, cwd=KOTLIN_DIR)


if __name__ == "__main__":
    unittest.main()
