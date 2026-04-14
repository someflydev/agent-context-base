import unittest
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent

class TestParityRunnerExists(unittest.TestCase):
    def setUp(self):
        self.runner_path = ROOT / "verification" / "faker" / "run_parity_check.py"

    def test_runner_exists(self):
        self.assertTrue(self.runner_path.exists())

    def test_runner_has_shebang_or_main(self):
        content = self.runner_path.read_text()
        self.assertTrue("__main__" in content or "#!/usr/bin/env python3" in content)

    def test_runner_documents_skip_behavior(self):
        content = self.runner_path.read_text()
        self.assertTrue("SKIP" in content)

    def test_runner_checks_python_reference(self):
        content = self.runner_path.read_text()
        self.assertTrue("check_python_reference" in content or "generation_patterns" in content)

if __name__ == "__main__":
    unittest.main()
