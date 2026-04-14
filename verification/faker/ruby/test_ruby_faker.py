import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestRubyFakerExample(unittest.TestCase):
    def setUp(self):
        self.ruby_dir = Path(__file__).parent.parent.parent.parent / "examples" / "canonical-faker" / "ruby"

    def test_gemfile_exists(self):
        gemfile = self.ruby_dir / "Gemfile"
        self.assertTrue(gemfile.exists())
        content = gemfile.read_text()
        self.assertIn("faker", content)
        self.assertIn("ffaker", content)

    def test_domain_types_defined(self):
        domain_rb = self.ruby_dir / "lib" / "domain.rb"
        self.assertTrue(domain_rb.exists())
        content = domain_rb.read_text()
        self.assertIn("Organization", content)
        self.assertIn("AuditEvent", content)

    def test_faker_pipeline_sets_seed(self):
        pipeline_rb = self.ruby_dir / "lib" / "faker_pipeline.rb"
        self.assertTrue(pipeline_rb.exists())
        content = pipeline_rb.read_text()
        self.assertIn("Faker::Config.random", content)

    def test_ffaker_contrast_documented(self):
        readme = self.ruby_dir / "README.md"
        self.assertTrue(readme.exists())
        content = readme.read_text()
        self.assertIn("ffaker", content)
        self.assertTrue("locale" in content or "contrast" in content or "faster" in content)
        
        ffaker_pipeline = self.ruby_dir / "lib" / "ffaker_pipeline.rb"
        self.assertTrue(ffaker_pipeline.exists())
        content = ffaker_pipeline.read_text()
        self.assertIn("FFaker", content)

    def test_alice_not_required(self):
        for root, _, files in os.walk(self.ruby_dir):
            for file in files:
                if file.endswith((".rb", ".md", "Gemfile")):
                    content = (Path(root) / file).read_text().lower()
                    self.assertNotIn("alice", content, f"Alice found in {file}")

    def test_ruby_build_if_available(self):
        try:
            ruby_version = subprocess.run(["ruby", "-e", "puts RUBY_VERSION"], check=True, capture_output=True, text=True).stdout.strip()
            if ruby_version < "2.7":
                self.skipTest(f"ruby >= 2.7 required, found {ruby_version}")
            subprocess.run(["bundle", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("ruby or bundle not found")
        
        subprocess.run(["bundle", "install", f"--gemfile={self.ruby_dir / 'Gemfile'}"], check=True)

    def test_ruby_smoke_if_available(self):
        try:
            ruby_version = subprocess.run(["ruby", "-e", "puts RUBY_VERSION"], check=True, capture_output=True, text=True).stdout.strip()
            if ruby_version < "2.7":
                self.skipTest(f"ruby >= 2.7 required, found {ruby_version}")
            subprocess.run(["bundle", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("ruby or bundle not found")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["bundle", "exec", "ruby", "generate.rb", "--profile", "smoke", "--output", tmpdir],
                cwd=self.ruby_dir,
                check=True
            )
            out_file = Path(tmpdir) / "organizations.jsonl"
            self.assertTrue(out_file.exists())


if __name__ == "__main__":
    unittest.main()
