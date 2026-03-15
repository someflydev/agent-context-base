from __future__ import annotations

import ast
import unittest

from verification.helpers import REPO_ROOT, load_python_module, python_api_stub_modules


INCLUDE_EXCLUDE_PATH = REPO_ROOT / "examples/canonical-api/fastapi-include-exclude-filter-example.py"
COUNTS_PATH = REPO_ROOT / "examples/canonical-api/fastapi-dynamic-counts-fragment-example.py"
FRAGMENT_PATH = REPO_ROOT / "examples/canonical-api/fastapi-faceted-filter-fragment-example.py"
PLOTLY_PATH = REPO_ROOT / "examples/canonical-api/fastapi-plotly-query-endpoint-example.py"
RUNTIME_PATH = REPO_ROOT / "examples/canonical-api/fastapi-example/app.py"
SPLIT_PANEL_PATH = REPO_ROOT / "examples/canonical-api/fastapi-split-filter-panel-example.py"
PLAYWRIGHT_FILTERING_PATH = REPO_ROOT / "examples/canonical-integration-tests/playwright-backend-filtering-example.spec.ts"
PLAYWRIGHT_COUNTS_PATH = REPO_ROOT / "examples/canonical-integration-tests/playwright-filter-counts-example.spec.ts"
PLAYWRIGHT_SPLIT_PANEL_PATH = REPO_ROOT / "examples/canonical-integration-tests/playwright-split-filter-panel-example.spec.ts"


def load_example(path, module_name: str):
    return load_python_module(path, module_name=module_name, stub_modules=python_api_stub_modules())


class BackendDrivenUIExampleTests(unittest.TestCase):
    def test_example_files_parse(self) -> None:
        for path in (INCLUDE_EXCLUDE_PATH, COUNTS_PATH, FRAGMENT_PATH, PLOTLY_PATH, RUNTIME_PATH, SPLIT_PANEL_PATH):
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


class SplitFilterPanelExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_example(SPLIT_PANEL_PATH, "verification.examples.python.split_filter_panel")

    def test_include_count_zero_when_value_excluded(self) -> None:
        state = self.module.build_query_state(status_out=["archived"])
        html = self.module.render_split_filter_panel(state)
        # Include option for archived must have count 0 and data-excluded="true"
        self.assertIn(
            'data-filter-option="archived" data-filter-mode="include" data-option-count="0" data-excluded="true"',
            html,
        )

    def test_exclude_impact_count_correct(self) -> None:
        state = self.module.build_query_state(status_out=["archived"])
        counts = self.module.exclude_impact_counts(state, "status")
        # archived has 1 row (legacy-import)
        self.assertEqual(counts["archived"], 1)

    def test_exclude_impact_count_with_team_filter(self) -> None:
        state = self.module.build_query_state(status_out=["paused"], team_in=["platform"])
        counts = self.module.exclude_impact_counts(state, "status")
        # platform+paused = api-latency only → 1
        self.assertEqual(counts["paused"], 1)

    def test_quick_exclude_active_in_main_section(self) -> None:
        state = self.module.build_query_state(status_out=["archived"])
        html = self.module.render_split_filter_panel(state)
        # Quick exclude toggle must be active
        self.assertIn(
            'data-role="quick-exclude" data-quick-exclude-dimension="status" '
            'data-quick-exclude-value="archived" data-active="true"',
            html,
        )
        # Main section exclude option must be active and checked
        self.assertIn(
            'data-filter-option="archived" data-filter-mode="exclude" '
            'data-option-count="1" data-active="true"',
            html,
        )
        self.assertIn(
            'name="status_out" value="archived" checked',
            html,
        )

    def test_quick_exclude_inactive_when_not_excluded(self) -> None:
        state = self.module.build_query_state()
        html = self.module.render_split_filter_panel(state)
        # Quick exclude for archived must not be active
        self.assertNotIn(
            'data-quick-exclude-value="archived" data-active="true"',
            html,
        )
        # Include option for archived must not carry data-excluded
        self.assertNotIn(
            'data-filter-option="archived" data-filter-mode="include" data-option-count="0" data-excluded="true"',
            html,
        )

    def test_playwright_split_panel_spec_covers_all_rules(self) -> None:
        spec = PLAYWRIGHT_SPLIT_PANEL_PATH.read_text(encoding="utf-8")
        # RULE 1
        self.assertIn('data-excluded', spec)
        self.assertIn('toBeDisabled', spec)
        # RULE 2
        self.assertIn('data-active', spec)
        self.assertIn('toBeChecked', spec)
        # RULE 3
        self.assertIn('data-role="quick-exclude"', spec)
        self.assertIn('data-quick-exclude-value', spec)


if __name__ == "__main__":
    unittest.main()
