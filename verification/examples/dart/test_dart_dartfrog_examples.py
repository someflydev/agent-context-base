from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.dart_dartfrog_min_app.verify import docker_smoke_check


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/dart-dartfrog-api-endpoint-example.dart"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/dart-dartfrog-html-fragment-example.dart"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/dart-dartfrog-data-endpoint-example.dart"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/dart-dartfrog-source-sync-example.dart"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/dart-dartfrog-example"


class DartDartFrogExampleTests(unittest.TestCase):
    def test_api_example_contains_dart_frog_route_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("import 'package:dart_frog/dart_frog.dart';", text)
        self.assertIn("context.request.uri.queryParameters['window'] ?? '24h'", text)
        self.assertIn("Response.json(", text)
        self.assertIn("'tenant_id': tenantId", text)

    def test_fragment_example_contains_htmx_markers(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('class="report-card"', text)
        self.assertIn('hx-swap-oob="true"', text)
        self.assertIn("'content-type': 'text/html; charset=utf-8'", text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("'metric': metric", text)
        self.assertIn("{'x': '2026-03-01', 'y': 18}", text)
        self.assertIn("Response.json(body: chartPayload(metric))", text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("abstract interface class ReleaseSourceClient", text)
        self.assertIn("Future<RawCapture> archiveRawCapture", text)
        self.assertIn("Future<List<NormalizedReleaseRecord>> replayFromArchive", text)
        self.assertIn("context.request.method != HttpMethod.post", text)
        self.assertIn("'raw_capture_path': rawPath", text)
        self.assertIn("checkpointToken", text)

    def test_data_acquisition_readme_references_dart_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("dart-dartfrog-source-sync-example.dart (structure-verified)", text)
        self.assertIn("real Dart example, `structure-verified` only", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in (
            "pubspec.yaml",
            "Dockerfile",
            "README.md",
            "routes/index.dart",
            "routes/healthz.dart",
            "routes/api/reports/[tenant_id].dart",
            "routes/fragments/report-card/[tenant_id].dart",
            "routes/data/chart/[metric].dart",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "dart-dartfrog-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["api_payload"]["window"], "24h")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
