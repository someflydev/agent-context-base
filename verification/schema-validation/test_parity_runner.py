from __future__ import annotations

from pathlib import Path
import unittest


RUNNER = (
    Path(__file__).resolve().parent / "run_parity_check.py"
)


class TestParityRunnerExists(unittest.TestCase):
    def test_parity_runner_script_exists(self) -> None:
        self.assertTrue(RUNNER.exists(), "expected run_parity_check.py to exist")

    def test_parity_runner_is_executable(self) -> None:
        content = RUNNER.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("#!/usr/bin/env python3") or "__main__" in content)

    def test_parity_runner_documents_scope_boundary(self) -> None:
        content = RUNNER.read_text(encoding="utf-8")
        self.assertTrue("toolchain" in content or "SKIP" in content)


if __name__ == "__main__":
    unittest.main()
