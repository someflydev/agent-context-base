from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.phoenix_min_app.verify import docker_smoke_check, native_smoke_check


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


MINI_APP_DIR = REPO_ROOT / "examples/canonical-api/phoenix-example"


class PhoenixMiniAppTests(unittest.TestCase):
    def test_mini_app_directory_exists(self) -> None:
        self.assertTrue(MINI_APP_DIR.is_dir())

    def test_mix_exs_present(self) -> None:
        self.assertTrue((MINI_APP_DIR / "mix.exs").is_file())

    def test_dockerfile_present(self) -> None:
        self.assertTrue((MINI_APP_DIR / "Dockerfile").is_file())

    def test_router_has_healthz_route(self) -> None:
        text = (MINI_APP_DIR / "lib/example_web/router.ex").read_text(encoding="utf-8")
        self.assertIn("/healthz", text)

    def test_router_has_api_reports_route(self) -> None:
        text = (MINI_APP_DIR / "lib/example_web/router.ex").read_text(encoding="utf-8")
        self.assertIn("/api/reports/:tenant_id", text)

    def test_router_has_fragment_route(self) -> None:
        text = (MINI_APP_DIR / "lib/example_web/router.ex").read_text(encoding="utf-8")
        self.assertIn("/fragments", text)
        self.assertIn("report-card", text)

    def test_fragment_controller_has_hx_swap_oob(self) -> None:
        text = (MINI_APP_DIR / "lib/example_web/controllers/fragment_controller.ex").read_text(
            encoding="utf-8"
        )
        self.assertIn('hx-swap-oob="true"', text)

    def test_reporting_context_module_present(self) -> None:
        self.assertTrue((MINI_APP_DIR / "lib/example/reporting.ex").is_file())

    def test_optional_native_mix_build(self) -> None:
        native_smoke_check()

    def test_optional_docker_phoenix_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["payload"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
