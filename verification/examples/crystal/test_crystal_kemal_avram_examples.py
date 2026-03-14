from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.crystal_kemal_avram_min_app.verify import docker_smoke_check


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/crystal-kemal-avram-api-endpoint-example.cr"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/crystal-kemal-avram-html-fragment-example.cr"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/crystal-kemal-avram-data-endpoint-example.cr"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/crystal-kemal-source-sync-example.cr"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/crystal-kemal-avram-example"


class CrystalKemalAvramExampleTests(unittest.TestCase):
    def test_api_example_contains_kemal_and_avram_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/api/reports/:tenant_id" do |env|', text)
        self.assertIn("class ReportSnapshotQuery < ReportSnapshot::BaseQuery", text)
        self.assertIn('ReportEnvelope.new(', text)
        self.assertIn('"crystal-kemal-avram"', text)

    def test_fragment_example_contains_htmx_fragment_surface(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/fragments/report-card/:tenant_id" do |env|', text)
        self.assertIn("class ReportSnapshotQuery < ReportSnapshot::BaseQuery", text)
        self.assertIn('class="report-card"', text)
        self.assertIn("hx-swap-oob", text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/data/chart/:metric" do |env|', text)
        self.assertIn("class MetricPointQuery < MetricPoint::BaseQuery", text)
        self.assertIn('SeriesPoint.new("2026-03-01", 18)', text)
        self.assertIn("MetricSeries.new(metric, points)", text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("class SourceCheckpointQuery < SourceCheckpoint::BaseQuery", text)
        self.assertIn("def archive_raw_capture", text)
        self.assertIn("def replay_from_archive", text)
        self.assertIn("getter external_slug : String", text)
        self.assertIn('post "/sources/github-releases/:owner/:repo/sync" do |env|', text)

    def test_data_acquisition_readme_references_crystal_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("crystal-kemal-source-sync-example.cr (structure-verified)", text)
        self.assertIn("real Crystal example, `structure-verified` only", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in ("shard.yml", "Dockerfile", "README.md", "src/app.cr"):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_runtime_bundle_declares_kemal_and_avram_dependencies(self) -> None:
        text = (RUNTIME_DIR / "shard.yml").read_text(encoding="utf-8")
        self.assertIn("kemal:", text)
        self.assertIn("github: kemalcr/kemal", text)
        self.assertIn("avram:", text)
        self.assertIn("github: luckyframework/avram", text)

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "crystal-kemal-avram-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["api_payload"]["service"], "crystal-kemal-avram-example")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
