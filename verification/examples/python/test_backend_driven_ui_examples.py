from __future__ import annotations

import ast
import unittest

from verification.helpers import REPO_ROOT, load_python_module, python_api_stub_modules


INCLUDE_EXCLUDE_PATH = REPO_ROOT / "examples/canonical-api/fastapi-include-exclude-filter-example.py"
COUNTS_PATH = REPO_ROOT / "examples/canonical-api/fastapi-dynamic-counts-fragment-example.py"
FRAGMENT_PATH = REPO_ROOT / "examples/canonical-api/fastapi-faceted-filter-fragment-example.py"
PLOTLY_PATH = REPO_ROOT / "examples/canonical-api/fastapi-plotly-query-endpoint-example.py"
RUNTIME_PATH = REPO_ROOT / "examples/canonical-api/fastapi-example/app.py"
PLAYWRIGHT_FILTERING_PATH = REPO_ROOT / "examples/canonical-integration-tests/playwright-backend-filtering-example.spec.ts"
PLAYWRIGHT_COUNTS_PATH = REPO_ROOT / "examples/canonical-integration-tests/playwright-filter-counts-example.spec.ts"


def load_example(path, module_name: str):
    return load_python_module(path, module_name=module_name, stub_modules=python_api_stub_modules())


class BackendDrivenUIExampleTests(unittest.TestCase):
    def test_example_files_parse(self) -> None:
        for path in (INCLUDE_EXCLUDE_PATH, COUNTS_PATH, FRAGMENT_PATH, PLOTLY_PATH, RUNTIME_PATH):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"))

    def test_include_exclude_endpoint_returns_expected_rows(self) -> None:
        module = load_example(INCLUDE_EXCLUDE_PATH, "verification.examples.python.include_exclude")
        payload = module.search_reports(team_in=["growth"], status_out=["archived"])
        self.assertEqual(payload["result_count"], 3)
        self.assertEqual(
            [row["report_id"] for row in payload["items"]],
            ["daily-signups", "trial-conversions", "checkout-failures"],
        )
        self.assertEqual(payload["filters"]["status_out"], ["archived"])

    def test_dynamic_counts_follow_documented_semantics(self) -> None:
        module = load_example(COUNTS_PATH, "verification.examples.python.dynamic_counts")
        state = module.build_query_state(team_in=["growth"], status_out=["archived"])
        self.assertEqual(module.facet_counts(state, "team"), {"growth": 3, "platform": 2})
        self.assertEqual(module.facet_counts(state, "region"), {"us": 2, "eu": 1, "apac": 0})
        html = module.render_filter_panel(state)
        self.assertIn('data-filter-dimension="team"', html)
        self.assertIn('data-option-count="2"', html)
        self.assertIn("backend query semantics", html)

    def test_fragment_response_exposes_backend_state(self) -> None:
        module = load_example(FRAGMENT_PATH, "verification.examples.python.fragment")
        response = module.report_results(team_in=["growth"], status_out=["archived"], region_in=["us"])
        html = response.content
        self.assertIn('data-result-count="2"', html)
        self.assertIn('data-query-fingerprint="team_in=growth|team_out=|status_in=|status_out=archived|region_in=us|region_out="', html)
        self.assertIn('data-report-id="daily-signups"', html)
        self.assertIn('data-role="active-filters"', html)

    def test_plotly_payload_stays_aligned_with_filtered_rows(self) -> None:
        module = load_example(PLOTLY_PATH, "verification.examples.python.plotly")
        payload = module.report_chart(team_in=["growth"], status_out=["archived"])
        self.assertEqual(payload["result_count"], 3)
        self.assertEqual(payload["totals"]["events"], 28)
        self.assertEqual(payload["plotly"]["data"][0]["x"], ["2026-03-01", "2026-03-02", "2026-03-03"])
        self.assertEqual(payload["plotly"]["data"][0]["y"], [12, 7, 9])

    def test_runtime_bundle_keeps_fragments_counts_and_chart_in_sync(self) -> None:
        module = load_example(RUNTIME_PATH, "verification.examples.python.runtime_ui")
        state = module.build_query_state(team_in=["growth"], status_out=["archived"])
        rows = module.filter_rows(state)
        counts_html = module.render_filter_panel_html(state)
        results_html = module.render_results_fragment_html(state)
        chart = module.build_chart_payload(state)
        self.assertEqual(len(rows), 3)
        self.assertEqual(chart["result_count"], len(rows))
        self.assertIn('data-role="count-discipline"', counts_html)
        self.assertIn('data-result-count="3"', results_html)
        self.assertEqual(chart["filters"]["team_in"], ["growth"])

    def test_playwright_examples_assert_semantics(self) -> None:
        filtering = PLAYWRIGHT_FILTERING_PATH.read_text(encoding="utf-8")
        counts = PLAYWRIGHT_COUNTS_PATH.read_text(encoding="utf-8")
        self.assertIn("chart.result_count", filtering)
        self.assertIn("toHaveText(\"3 results\")", filtering)
        self.assertIn("toHaveText(\"2\")", counts)
        self.assertIn('data-role="count-discipline"', counts)


if __name__ == "__main__":
    unittest.main()
