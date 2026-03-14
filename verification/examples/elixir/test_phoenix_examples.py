from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT


ROUTER_PATH = REPO_ROOT / "examples/canonical-api/phoenix-router-surface-example.ex"
CONTROLLER_PATH = REPO_ROOT / "examples/canonical-api/phoenix-route-controller-example.ex"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/phoenix-source-sync-example.ex"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"


class PhoenixExampleTests(unittest.TestCase):
    def test_router_contains_expected_route(self) -> None:
        text = ROUTER_PATH.read_text(encoding="utf-8")
        self.assertIn('get "/tenants/:tenant_id/reports", ReportController, :index', text)
        self.assertIn("pipe_through :browser", text)

    def test_controller_contains_expected_render_path(self) -> None:
        text = CONTROLLER_PATH.read_text(encoding="utf-8")
        self.assertIn('render(conn, :index, tenant_id: tenant_id, summaries: summaries)', text)
        self.assertIn("Reporting.list_recent_reports", text)

    def test_router_and_controller_reference_same_surface(self) -> None:
        router_text = ROUTER_PATH.read_text(encoding="utf-8")
        controller_text = CONTROLLER_PATH.read_text(encoding="utf-8")
        self.assertIn("ReportController", router_text)
        self.assertIn("defmodule ExampleWeb.ReportController", controller_text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("defmodule Example.Acquisition.GitHubReleaseSyncService do", text)
        self.assertIn("def archive_raw_capture", text)
        self.assertIn("def replay_from_archive", text)
        self.assertIn("external_slug: external_slug", text)
        self.assertIn('def create(conn, %{"owner" => owner, "repo" => repo} = params) do', text)

    def test_data_acquisition_readme_references_elixir_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("phoenix-source-sync-example.ex (structure-verified)", text)
        self.assertIn("real Elixir example, `structure-verified` only", text)


if __name__ == "__main__":
    unittest.main()
