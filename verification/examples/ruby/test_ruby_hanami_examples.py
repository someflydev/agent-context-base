from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.ruby_hanami_min_app.verify import docker_smoke_check


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/ruby-hanami-api-endpoint-example.rb"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/ruby-hanami-html-fragment-example.rb"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/ruby-hanami-data-endpoint-example.rb"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/ruby-hanami-source-sync-example.rb"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/ruby-hanami-example"


class RubyHanamiExampleTests(unittest.TestCase):
    def test_api_example_contains_router_action_and_sequel_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/api/reports/:tenant_id", to: ShowReport.new', text)
        self.assertIn("class ShowReport < Hanami::Action", text)
        self.assertIn('service: "ruby-hanami"', text)
        self.assertIn("DB[:reports].where(tenant_id: tenant_id).first", text)

    def test_fragment_example_contains_view_rendering_surface(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/fragments/report-card/:tenant_id", to: ShowReportCard.new', text)
        self.assertIn("class ReportCardView < Hanami::View", text)
        self.assertIn("config.layout = false", text)
        self.assertIn("ReportCardView.new.call", text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/data/chart/:metric", to: ShowChart.new', text)
        self.assertIn("DB[:metric_points].where(metric: metric).order(:bucket_day).all", text)
        self.assertIn('metric: metric,', text)
        self.assertIn("points: MetricsRepo.series_for(metric)", text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("class SourceCheckpointsRepo", text)
        self.assertIn("class NormalizeReleasePayload", text)
        self.assertIn("def archive_raw_capture", text)
        self.assertIn("def replay_from_archive", text)
        self.assertIn('post "/source-sync/:owner/:repo", to: SourceSyncAction.new', text)
        self.assertIn("checkpoint_token:", text)

    def test_data_acquisition_readme_references_ruby_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("ruby-hanami-source-sync-example.rb (structure-verified)", text)
        self.assertIn("real Ruby example, `structure-verified` only", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in (
            "Gemfile",
            "Dockerfile",
            "README.md",
            "app/router.rb",
            "app/actions/reports/show.rb",
            "app/actions/report_cards/show.rb",
            "app/actions/charts/show.rb",
            "app/views/report_cards/show.rb",
            "app/templates/report_cards/show.html.erb",
            "lib/ruby_hanami_example/persistence.rb",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_runtime_bundle_declares_hanami_and_sequel_dependencies(self) -> None:
        text = (RUNTIME_DIR / "Gemfile").read_text(encoding="utf-8")
        self.assertIn('gem "hanami-router"', text)
        self.assertIn('gem "hanami-controller"', text)
        self.assertIn('gem "hanami-view"', text)
        self.assertIn('gem "sequel"', text)
        self.assertIn('gem "sqlite3"', text)

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "ruby-hanami-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["api_payload"]["service"], "ruby-hanami-example")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
