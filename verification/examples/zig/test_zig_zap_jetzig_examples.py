from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.zig_zap_jetzig_min_app.verify import docker_smoke_check


JSON_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/zig-zap-json-endpoint-example.zig"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/zig-jetzig-html-fragment-example.zig"
FRAGMENT_TEMPLATE_PATH = REPO_ROOT / "examples/canonical-api/zig-jetzig-html-fragment-template-example.zmpl"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/zig-zap-data-endpoint-example.zig"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/zig-zap-jetzig-example"


class ZigZapJetzigExampleTests(unittest.TestCase):
    def test_json_example_contains_expected_route_surface(self) -> None:
        text = JSON_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('"/api/health"', text)
        self.assertIn('snapshot.service', text)
        self.assertIn('r.setContentType(.JSON)', text)

    def test_fragment_example_contains_jetzig_render_surface(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('@import("jetzig")', text)
        self.assertIn('request.renderTemplate("reports/summary_fragment", .ok)', text)
        self.assertIn('"/reports/summary_fragment"', text)
        self.assertTrue(FRAGMENT_TEMPLATE_PATH.exists())

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('const prefix = "/data/series/";', text)
        self.assertIn('\\"points\\":[', text)
        self.assertIn('buildSeriesPayload(metric, &buf)', text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in ("main.zig", "build.zig", "build.zig.zon", "Dockerfile", "README.md"):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "zig-zap-jetzig-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
