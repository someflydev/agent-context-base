from __future__ import annotations

import os
import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.kotlin_http4k_exposed_min_app.verify import (
    docker_smoke_check,
    native_smoke_check,
)


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/kotlin-http4k-exposed-api-endpoint-example.kt"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/kotlin-http4k-exposed-html-fragment-example.kt"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/kotlin-http4k-exposed-data-endpoint-example.kt"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/kotlin-http4k-source-sync-example.kt"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/kotlin-http4k-exposed-example"


class KotlinHttp4kExposedExampleTests(unittest.TestCase):
    def test_api_example_contains_http4k_and_exposed_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('"/api/reports/{tenantId}" bind GET', text)
        self.assertIn("Body.auto<ReportEnvelope>().toLens()", text)
        self.assertIn(".select { Reports.tenantId eq tenantId }", text)

    def test_fragment_example_contains_htmx_markers(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('"/fragments/report-card/{tenantId}" bind GET', text)
        self.assertIn('class="report-card"', text)
        self.assertIn("hx-swap-oob", text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('"/data/chart/{metric}" bind GET', text)
        self.assertIn("ChartPayload(", text)
        self.assertIn('SeriesPoint("2026-03-01", 18)', text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("data class SyncCursor(", text)
        self.assertIn("class SourceCheckpointRepository", text)
        self.assertIn("fun archiveRawCapture", text)
        self.assertIn("fun replayFromArchive", text)
        self.assertIn('"/source-sync/{owner}/{repo}" bind POST', text)
        self.assertIn("ReleaseProvenance(", text)

    def test_data_acquisition_readme_references_kotlin_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("kotlin-http4k-source-sync-example.kt (structure-verified)", text)
        self.assertIn("real Kotlin example, `structure-verified` only", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in (
            "build.gradle.kts",
            "settings.gradle.kts",
            "Dockerfile",
            "README.md",
            "src/main/kotlin/example/Main.kt",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_native_kotlin_compile(self) -> None:
        if os.environ.get("VERIFY_HEAVY_NATIVE", "").strip().lower() not in {"1", "true", "yes", "on"}:
            self.skipTest("native Kotlin build is reserved for heavy verification")
        native_smoke_check()

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "kotlin-http4k-exposed-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenantId"], "acme")
        self.assertEqual(payload["api_payload"]["service"], "kotlin-http4k-exposed-example")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
