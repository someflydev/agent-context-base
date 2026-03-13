from __future__ import annotations

import os
import re
import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.go_echo_min_app.verify import docker_smoke_check, native_smoke_check


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/go-echo-handler-example.go"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/go-echo-example"


class GoEchoExampleTests(unittest.TestCase):
    def test_handler_source_contains_expected_route_shape(self) -> None:
        text = EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r'group\.GET\("/tenants/:tenantID/reports",\s*handler\.ListRecent\)')
        self.assertIn("views.ReportSummaryList", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in ("main.go", "go.mod", "Dockerfile", "README.md"):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_native_go_build(self) -> None:
        if os.environ.get("VERIFY_HEAVY_NATIVE", "").strip().lower() not in {"1", "true", "yes", "on"}:
            self.skipTest("native Go build is reserved for heavy verification")
        native_smoke_check()

    def test_optional_docker_go_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["payload"], {"status": "ok", "service": "go-echo-example"})


if __name__ == "__main__":
    unittest.main()
