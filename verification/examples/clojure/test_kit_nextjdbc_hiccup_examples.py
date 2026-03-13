from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.clojure_kit_nextjdbc_hiccup_min_app.verify import docker_smoke_check


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/clojure-kit-nextjdbc-hiccup-api-endpoint-example.clj"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/clojure-kit-nextjdbc-hiccup-html-fragment-example.clj"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/clojure-kit-nextjdbc-hiccup-data-endpoint-example.clj"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/clojure-kit-nextjdbc-hiccup-example"


class ClojureKitNextJdbcHiccupExampleTests(unittest.TestCase):
    def test_api_example_contains_next_jdbc_query_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('"/api/reports/:tenant-id"', text)
        self.assertIn("jdbc/execute-one!", text)
        self.assertIn('"select report_id, total_events, status from reports where tenant_id = ?"', text)

    def test_fragment_example_contains_hiccup_fragment_surface(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("hiccup2.core", text)
        self.assertIn('"/fragments/report-card/:tenant-id"', text)
        self.assertIn('hx-swap-oob "true"', text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('"/data/chart/:metric"', text)
        self.assertIn("jdbc/execute!", text)
        self.assertIn(":points points", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in (
            "deps.edn",
            "Dockerfile",
            "README.md",
            "src/clojure_kit_nextjdbc_hiccup_example/core.clj",
            "src/clojure_kit_nextjdbc_hiccup_example/routes.clj",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "clojure-kit-nextjdbc-hiccup-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
