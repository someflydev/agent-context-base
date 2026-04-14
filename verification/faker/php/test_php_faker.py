import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPhpFakerExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent.parent.parent
        cls.php_dir = cls.root_dir / "examples" / "canonical-faker" / "php"

    def test_composer_json_exists(self):
        composer_json_path = self.php_dir / "composer.json"
        self.assertTrue(composer_json_path.exists())
        content = composer_json_path.read_text(encoding="utf-8")
        self.assertIn("fakerphp/faker", content)
        self.assertIn("nelmio/alice", content)

    def test_entity_classes_defined(self):
        entities_path = self.php_dir / "src" / "Domain" / "Entities.php"
        self.assertTrue(entities_path.exists())
        content = entities_path.read_text(encoding="utf-8")
        self.assertIn("readonly class Organization", content)

    def test_alice_fixtures_exist(self):
        alice_dir = self.php_dir / "alice"
        self.assertTrue((alice_dir / "organizations.yaml").exists())
        self.assertTrue((alice_dir / "memberships.yaml").exists())

    def test_alice_readme_is_honest(self):
        readme_path = self.php_dir / "alice" / "README.md"
        self.assertTrue(readme_path.exists())
        content = readme_path.read_text(encoding="utf-8")
        self.assertTrue("temporal" in content or "weighted" in content)
        self.assertIn("NOT", content)

    def test_pipeline_uses_unique_faker(self):
        pipeline_path = self.php_dir / "src" / "Pipeline" / "TenantCorePipeline.php"
        self.assertTrue(pipeline_path.exists())
        content = pipeline_path.read_text(encoding="utf-8")
        self.assertIn("unique()", content)

    def test_php_build_if_available(self):
        composer_path = shutil.which("composer")
        if not composer_path:
            self.skipTest("composer not found")
        result = subprocess.run(
            [composer_path, "install", "--working-dir=" + str(self.php_dir), "--no-interaction"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"composer install failed: {result.stderr}")

    def test_php_smoke_if_available(self):
        php_path = shutil.which("php")
        if not php_path:
            self.skipTest("php not found")
            
        composer_path = shutil.which("composer")
        if not composer_path:
            self.skipTest("composer not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            generate_script = self.php_dir / "generate.php"
            result = subprocess.run(
                [php_path, str(generate_script), "--profile", "smoke", "--output", tmpdir],
                capture_output=True,
                text=True,
                cwd=self.php_dir,
            )
            self.assertEqual(result.returncode, 0, f"generate.php failed: {result.stderr}")
            self.assertTrue((Path(tmpdir) / "organizations.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
