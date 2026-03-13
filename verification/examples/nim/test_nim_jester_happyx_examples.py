from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.nim_jester_happyx_min_app.verify import docker_smoke_check


JSON_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/nim-jester-json-endpoint-example.nim"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/nim-happyx-html-fragment-example.nim"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/nim-jester-data-endpoint-example.nim"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/nim-jester-happyx-example"


class NimJesterHappyXExampleTests(unittest.TestCase):
    def test_json_example_contains_expected_route_surface(self) -> None:
        text = JSON_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/api/health"', text)
        self.assertIn('resp %*{', text)
        self.assertIn('service: "nim-jester-happyx"', text)

    def test_fragment_example_contains_happyx_component_and_route(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("import happyx", text)
        self.assertIn("component ReportSummaryCard:", text)
        self.assertIn('get "/fragments/report-summary/@tenantId"', text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/data/series/@metric"', text)
        self.assertIn('"points": [', text)
        self.assertIn('"metric": metric', text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in ("main.nim", "Dockerfile", "README.md"):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "nim-jester-happyx-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
