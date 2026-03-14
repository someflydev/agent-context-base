from __future__ import annotations

import os
import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.scala_tapir_http4s_zio_min_app.verify import (
    docker_smoke_check,
    native_smoke_check,
)


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/scala-tapir-http4s-zio-api-endpoint-example.scala"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/scala-tapir-http4s-zio-html-fragment-example.scala"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/scala-tapir-http4s-zio-data-endpoint-example.scala"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/scala-tapir-source-sync-example.scala"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/scala-tapir-http4s-zio-example"


class ScalaTapirHttp4sZioExampleTests(unittest.TestCase):
    def test_api_example_contains_typed_tapir_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('in("api" / "tenants" / path[String]("tenantId") / "reports")', text)
        self.assertIn("query[Option[Int]](\"limit\")", text)
        self.assertIn("listReportsEndpoint.serverLogicSuccess[Task]", text)

    def test_fragment_example_contains_http4s_fragment_surface(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('Root / "fragments" / "report-card" / tenantId', text)
        self.assertIn('class="report-card"', text)
        self.assertIn("hx-swap-oob", text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('in("data" / "chart" / path[String]("metric"))', text)
        self.assertIn("ChartPayload(", text)
        self.assertIn('SeriesPoint("2026-03-01", 18)', text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("final case class SyncCursor(", text)
        self.assertIn("trait ReleaseSourceClient:", text)
        self.assertIn("def archiveRawCapture", text)
        self.assertIn("def replayFromArchive", text)
        self.assertIn('.in("source-sync")', text)
        self.assertIn("repository.save(records, nextCursor)", text)

    def test_data_acquisition_readme_references_scala_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("scala-tapir-source-sync-example.scala (structure-verified)", text)
        self.assertIn("real Scala example, `structure-verified` only", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in (
            "build.sbt",
            "Dockerfile",
            "README.md",
            "project/build.properties",
            "src/main/scala/Main.scala",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_native_scala_compile(self) -> None:
        if os.environ.get("VERIFY_HEAVY_NATIVE", "").strip().lower() not in {"1", "true", "yes", "on"}:
            self.skipTest("native Scala build is reserved for heavy verification")
        native_smoke_check()

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "scala-tapir-http4s-zio-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenantId"], "acme")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
