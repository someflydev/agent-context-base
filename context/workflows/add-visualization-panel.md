# Add Visualization Panel

## Purpose
Add a Plotly-backed chart panel to a server-rendered page with HTMX fragment support, Tailwind filter UI, and paired textual summary.

## When To Use It
- adding a new chart to an analytics workbench page
- refactoring inline chart construction into a proper figure-builder structure
- adding a drilldown or detail panel to an existing chart view

## Sequence

Step 1 — Select chart type.
Load `context/skills/chart-type-selection.md`. State the analysis question.
Do not proceed without a justified chart type choice.

Step 2 — Design the aggregation layer.
Define inputs (query state, filters) and outputs (structured aggregate data).
Write a unit test before implementing.

Step 3 — Design the figure builder.
Follow `context/skills/plotly-figure-builder-design.md` (three-layer model).
Set all mandatory figure fields. Write three unit tests (valid, empty, single-item).

Step 4 — Add the chart data endpoint.
The endpoint calls the aggregation layer then the figure builder.
It must accept the same filter state as the results endpoint.
Verify query state alignment with `backend-driven-ui-correctness.md`.

Step 5 — Add paired textual summary.
A summary card or subtitle must show: total count, date range, active filters.

Step 6 — Wire HTMX fragment with Tailwind filter controls.
Identify the smallest panel boundary for the chart + summary card.
Use `hx-target` and `hx-swap` to replace only that panel on filter change.
Multi-select filter inputs must follow `filter-panel-rendering-rules.md` class contract.
Verify server-rendered fallback without JavaScript.

Step 7 — Add smoke test.
Assert the chart endpoint returns 200 and the response contains a valid Plotly figure with at least one trace and a non-empty axis title.

Step 8 — Run verification.
`python3 scripts/run_verification.py --tier fast`

## Outputs
- aggregation function with unit test
- figure builder with three unit tests (valid, empty, single-item)
- chart data endpoint
- HTML template fragment (chart panel + summary card)
- HTMX fragment wiring in parent page template
- Tailwind multi-select filter form wired to fragment endpoint
- smoke test for chart endpoint

## Related Doctrine
- context/doctrine/plotly-htmx-server-rendered-viz.md
- context/doctrine/tailwind-utility-first.md
- context/doctrine/backend-driven-ui-correctness.md
- context/doctrine/filter-state-and-query-state.md
- context/doctrine/filter-panel-rendering-rules.md

## Common Pitfalls
- picking chart type before stating the analysis question
- chart endpoint applying different filter logic than results endpoint
- `hx-target` scoped too wide (replacing whole page instead of panel)
- no fallback HTML when JavaScript or HTMX is unavailable
- missing textual summary alongside chart
- figure builder that cannot be tested without a running server