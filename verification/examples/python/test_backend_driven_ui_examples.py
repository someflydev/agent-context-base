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
SEARCH_SORT_FILTER_PATH = REPO_ROOT / "examples/canonical-api/fastapi-search-sort-filter-example.py"
PLAYWRIGHT_CUJ_PATH = REPO_ROOT / "examples/canonical-integration-tests/playwright-cuj-filter-example.spec.ts"


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


class SearchSortFilterExampleTests(unittest.TestCase):
    """Unit tests for fastapi-search-sort-filter-example.py.

    Tests text search, sort, exclude-impact-count, facet-count, fingerprint,
    and rendering functions (RULE 1, RULE 2) using the shared REPORT_ROWS dataset.

    Dataset:
      daily-signups     growth   active   us    events=12
      trial-conversions growth   active   us    events=7
      api-latency       platform paused   eu    events=5
      checkout-failures growth   active   eu    events=9
      queue-depth       platform active   apac  events=11
      legacy-import     platform archived us    events=4
    """

    def setUp(self) -> None:
        self.module = load_example(
            SEARCH_SORT_FILTER_PATH,
            "verification.examples.python.search_sort_filter",
        )

    # -- filter_rows with text search --

    def test_filter_rows_with_text_search(self) -> None:
        # "signup" is a substring of "daily-signups" only — not of "trial-conversions"
        state = self.module.build_query_state(query="signup")
        rows = self.module.filter_rows(state)
        self.assertEqual(
            {r["report_id"] for r in rows},
            {"daily-signups"},
        )

    def test_filter_rows_search_and_facet_combined(self) -> None:
        state = self.module.build_query_state(query="latency", team_in=["platform"])
        rows = self.module.filter_rows(state)
        self.assertEqual({r["report_id"] for r in rows}, {"api-latency"})

    def test_filter_rows_search_and_exclude_combined(self) -> None:
        # api-latency is the only "api" row and it is paused → excluded
        state = self.module.build_query_state(query="api", status_out=["paused"])
        rows = self.module.filter_rows(state)
        self.assertEqual(rows, [])

    # -- facet_counts with text search --

    def test_facet_counts_respect_text_search(self) -> None:
        # "signup" matches only "daily-signups" (growth/active/us) → growth=1, platform=0
        state = self.module.build_query_state(query="signup")
        counts = self.module.facet_counts(state, "team")
        self.assertEqual(counts, {"growth": 1, "platform": 0})

    # -- exclude_impact_counts with text search --

    def test_exclude_impact_counts_respect_text_search(self) -> None:
        # search=signup: matches only daily-signups (growth/active/us)
        # That row is active; no paused or archived rows match "signup".
        # Excluding paused or archived removes 0 rows from the search-narrowed set.
        state = self.module.build_query_state(query="signup")
        counts = self.module.exclude_impact_counts(state, "status")
        self.assertEqual(counts["active"], 1)
        self.assertEqual(counts["paused"], 0)
        self.assertEqual(counts["archived"], 0)

    # -- sort_rows --

    def test_sort_events_desc(self) -> None:
        rows = self.module.sort_rows(self.module.REPORT_ROWS, "events_desc")
        self.assertEqual(rows[0]["report_id"], "daily-signups")   # events=12
        self.assertEqual(rows[-1]["report_id"], "legacy-import")  # events=4

    def test_sort_events_asc(self) -> None:
        rows = self.module.sort_rows(self.module.REPORT_ROWS, "events_asc")
        self.assertEqual(rows[0]["report_id"], "legacy-import")   # events=4
        self.assertEqual(rows[-1]["report_id"], "daily-signups")  # events=12

    def test_sort_name_asc(self) -> None:
        rows = self.module.sort_rows(self.module.REPORT_ROWS, "name_asc")
        # Alphabetically first among the six report IDs
        self.assertEqual(rows[0]["report_id"], "api-latency")

    def test_sort_unknown_defaults_to_events_desc(self) -> None:
        rows = self.module.sort_rows(self.module.REPORT_ROWS, "invalid_sort_value")
        self.assertEqual(rows[0]["report_id"], "daily-signups")   # events=12

    # -- fingerprint --

    def test_fingerprint_includes_query_and_sort(self) -> None:
        state = self.module.build_query_state(query="signup", sort="name_asc")
        fp = state.fingerprint()
        self.assertIn("query=signup", fp)
        self.assertIn("sort=name_asc", fp)

    # -- RULE 1: include greyed with search active --

    def test_rule1_holds_with_search_active(self) -> None:
        # With status_out=archived and query=signup, the archived include option
        # must have data-option-count="0" and data-excluded="true" (RULE 1 applies
        # regardless of whether the search narrows the dataset).
        state = self.module.build_query_state(
            status_out=["archived"], query="signup"
        )
        html = self.module.render_filter_panel_fragment(state)
        self.assertIn(
            'data-filter-option="archived" data-filter-mode="include" data-option-count="0" data-excluded="true"',
            html,
        )

    # -- RULE 2: exclude count can be 0 due to search, but option must NOT be disabled --

    def test_rule2_can_be_zero_due_to_search(self) -> None:
        # With status_out=archived and query=signup:
        # No "signup" rows are archived → exclude_impact_count for archived = 0.
        # The exclude option must show count=0 but must NOT have the disabled attribute.
        state = self.module.build_query_state(
            status_out=["archived"], query="signup"
        )
        html = self.module.render_filter_panel_fragment(state)
        # Exclude option must be active with count=0
        self.assertIn(
            'data-filter-option="archived" data-filter-mode="exclude" data-option-count="0" data-active="true"',
            html,
        )
        # The exclude option checkbox must NOT carry the disabled attribute
        # (count=0 does not mean disabled — the filter is active, just has no effect here)
        self.assertNotIn('name="status_out" value="archived" disabled', html)

    # -- CUJ spec structural check --

    def test_playwright_cuj_spec_covers_all_ten_cujs(self) -> None:
        spec = PLAYWRIGHT_CUJ_PATH.read_text(encoding="utf-8")
        # All 10 CUJ describe blocks must be present
        for cuj in [
            "CUJ-1",
            "CUJ-2",
            "CUJ-3",
            "CUJ-4",
            "CUJ-5",
            "CUJ-6",
            "CUJ-7",
            "CUJ-8",
            "CUJ-9",
            "CUJ-10",
        ]:
            self.assertIn(cuj, spec, f"{cuj} describe block missing from CUJ spec")
        # Page object model class must be present
        self.assertIn("class ReportsFilterPage", spec)
        self.assertIn("facetCount", spec)
        self.assertIn("quickExcludeActive", spec)
        self.assertIn("overflowY", spec)
        # Key assertion patterns
        self.assertIn('data-result-count="0"', spec)
        self.assertIn("data-query-fingerprint", spec)
        self.assertIn("filterPanelScrollTop", spec)
        self.assertIn("scrollFilterPanelTo", spec)


if __name__ == "__main__":
    unittest.main()
