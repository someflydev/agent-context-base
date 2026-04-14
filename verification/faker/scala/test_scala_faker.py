import unittest
import os
import subprocess
from pathlib import Path

class TestScalaFakerExample(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parents[3] / "examples" / "canonical-faker" / "scala"

    def test_build_sbt_exists(self):
        build_sbt = self.base_dir / "build.sbt"
        self.assertTrue(build_sbt.exists(), "build.sbt should exist")
        content = build_sbt.read_text(encoding="utf-8")
        self.assertIn("datafaker", content, "build.sbt should declare datafaker dependency")

    def test_ecosystem_note_in_readme(self):
        readme = self.base_dir / "README.md"
        self.assertTrue(readme.exists(), "README.md should exist")
        content = readme.read_text(encoding="utf-8").lower()
        self.assertTrue("scala-native" in content or "ecosystem" in content, "README should contain an honest ecosystem note")

    def test_lazy_list_in_pipeline(self):
        pipeline = self.base_dir / "src" / "main" / "scala" / "io" / "agentcontextbase" / "faker" / "Pipeline.scala"
        self.assertTrue(pipeline.exists(), "Pipeline.scala should exist")
        content = pipeline.read_text(encoding="utf-8")
        self.assertTrue("LazyList" in content or "Stream" in content or "Vector" in content, "Pipeline should use functional collections")

    def test_domain_case_classes_defined(self):
        domain = self.base_dir / "src" / "main" / "scala" / "io" / "agentcontextbase" / "faker" / "Domain.scala"
        self.assertTrue(domain.exists(), "Domain.scala should exist")
        content = domain.read_text(encoding="utf-8")
        self.assertIn("case class Organization", content)
        self.assertIn("case class AuditEvent", content)

    def test_validation_implemented(self):
        validate = self.base_dir / "src" / "main" / "scala" / "io" / "agentcontextbase" / "faker" / "Validate.scala"
        self.assertTrue(validate.exists(), "Validate.scala should exist")
        content = validate.read_text(encoding="utf-8")
        self.assertIn("ValidationReport", content)

    def test_scala_build_if_available(self):
        import shutil
        if not shutil.which("sbt"):
            self.skipTest("sbt not available")
        result = subprocess.run(["sbt", "compile"], cwd=self.base_dir, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"sbt compile failed:\n{result.stdout}\n{result.stderr}")

    def test_scala_smoke_if_available(self):
        import shutil
        if not shutil.which("sbt"):
            self.skipTest("sbt not available")
        result = subprocess.run(["sbt", "test"], cwd=self.base_dir, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"sbt test failed:\n{result.stdout}\n{result.stderr}")

if __name__ == '__main__':
    unittest.main()
