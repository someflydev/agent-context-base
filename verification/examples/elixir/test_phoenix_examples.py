from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT


ROUTER_PATH = REPO_ROOT / "examples/canonical-api/phoenix-router-surface-example.ex"
CONTROLLER_PATH = REPO_ROOT / "examples/canonical-api/phoenix-route-controller-example.ex"


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


if __name__ == "__main__":
    unittest.main()
