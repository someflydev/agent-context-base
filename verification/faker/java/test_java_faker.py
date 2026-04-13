from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
JAVA_DIR = REPO_ROOT / "examples" / "canonical-faker" / "java"


class TestJavaFakerExample(unittest.TestCase):
    def _maven_available(self) -> bool:
        if shutil.which("mvn") is None:
            return False
        java_check = subprocess.run(["mvn", "-version"], capture_output=True, text=True, check=False)
        return java_check.returncode == 0

    def test_pom_exists(self) -> None:
        path = JAVA_DIR / "pom.xml"
        self.assertTrue(path.exists())
        self.assertIn("datafaker", path.read_text(encoding="utf-8").lower())

    def test_entity_records_defined(self) -> None:
        path = JAVA_DIR / "src" / "main" / "java" / "io" / "agentcontextbase" / "faker" / "domain" / "TenantCoreEntities.java"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("record Organization", text)
        self.assertIn("record AuditEvent", text)

    def test_pipeline_uses_explicit_pools(self) -> None:
        path = JAVA_DIR / "src" / "main" / "java" / "io" / "agentcontextbase" / "faker" / "pipeline" / "TenantCorePipeline.java"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertTrue("orgIds" in text or "orgPool" in text)

    def test_maven_build_if_available(self) -> None:
        if not self._maven_available():
            self.skipTest("maven or a usable Java runtime is not installed")
        with tempfile.TemporaryDirectory() as repo_dir:
            try:
                subprocess.run(
                    ["mvn", "compile", "-f", str(JAVA_DIR / "pom.xml"), f"-Dmaven.repo.local={repo_dir}"],
                    check=True,
                    cwd=JAVA_DIR,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as exc:
                text = (exc.stdout or "") + (exc.stderr or "")
                if (
                    "Could not resolve host" in text
                    or "Temporary failure in name resolution" in text
                    or "Could not transfer artifact" in text
                    or "nodename nor servname provided" in text
                ):
                    self.skipTest("maven dependencies are not reachable in the current sandbox")
                raise

    def test_java_smoke_if_available(self) -> None:
        if not self._maven_available():
            self.skipTest("maven or a usable Java runtime is not installed")
        with tempfile.TemporaryDirectory() as repo_dir:
            try:
                subprocess.run(
                    ["mvn", "test", "-f", str(JAVA_DIR / "pom.xml"), "-Dtest=SmokeTest", f"-Dmaven.repo.local={repo_dir}"],
                    check=True,
                    cwd=JAVA_DIR,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as exc:
                text = (exc.stdout or "") + (exc.stderr or "")
                if (
                    "Could not resolve host" in text
                    or "Temporary failure in name resolution" in text
                    or "Could not transfer artifact" in text
                    or "nodename nor servname provided" in text
                ):
                    self.skipTest("maven dependencies are not reachable in the current sandbox")
                raise


if __name__ == "__main__":
    unittest.main()
