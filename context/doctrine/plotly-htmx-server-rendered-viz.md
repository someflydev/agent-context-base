# Plotly + HTMX Server-Rendered Visualization

## Purpose
This doctrine establishes Plotly and HTMX as the canonical approach for server-rendered analytics and visualization in this repository. It solves the problem of charts being treated as opaque, untestable client-side widgets by moving figure construction to the server. By constructing Plotly figures as structured data server-side and using HTMX for fragment updates, we ensure visualizations are testable, state-aligned, and deeply integrated with the application's backend architecture.

## Plotly as a Declarative Figure Model
Plotly figures are treated as structured data objects (traces, layout, configuration), not as rendered outputs. Server-side construction allows unit testing of chart logic independently of HTTP handlers or browser execution. The browser's Plotly.js library acts strictly as a rendering engine; it receives a fully-specified figure and does not make aggregation, layout, or formatting decisions.

## Rules

Rule 1 — Separate aggregation from figure construction.
Aggregation belongs in a service or query layer. Figure construction belongs in a dedicated figure-builder module. Handlers call both and return the result.

Rule 2 — Separate figure construction from serialization.
Figure builders return structured data (dict/struct/map). Serialization to JSON is done in the handler. This makes builders testable without HTTP.

Rule 3 — Choose chart type by analysis task, not by appearance.
The chart must answer a stated question. Use `context/skills/chart-type-selection.md` before choosing a chart type. Task and data shape drive the choice.

Rule 4 — Set intentional axis titles, hover content, and legend labels.
Axes must have titles. `hovertemplate` must be set on every trace. Legend labels must be human-readable. These are required fields, not styling.

Rule 5 — Derive chart data from the same query state as visible results.
Inherited from `backend-driven-ui-correctness.md`. The chart endpoint must never silently apply different filter logic than the results endpoint.

Rule 6 — Keep HTMX fragment boundaries at the panel, not the page.
Replace the smallest meaningful unit: one chart panel, one summary card, one detail drawer. Over-wide swaps mask filter-state bugs and inflate response size.

Rule 7 — Pair every chart with a fallback textual representation.
A summary card, table, or subtitle with key metrics must accompany any chart showing a trend, comparison, or distribution. Charts mislead without numerical context.

Rule 8 — Make figure output deterministic under deterministic seed data.
Figure builders receiving the same input must produce identical trace counts, axis ranges, and label sets. Non-determinism indicates hidden state or side effects.

Rule 9 — Avoid gratuitous 3D, excessive animation, and pie charts.
Use 3D only when the third dimension encodes necessary information. Use pie only for 2–3 part compositions. Do not add transitions or animations unless they aid comprehension.

Rule 10 — Never ship raw row-level datasets to the browser.
Aggregate server-side. The browser receives pre-computed traces, not event rows. Shipping raw rows couples the frontend to backend schema.

Rule 11 — Use Tailwind for all interactive filter UI state expression.
Active filter badges, disabled options, count badges, multi-select affordances, and drawer visibility must use Tailwind utilities. Follow `context/doctrine/filter-panel-rendering-rules.md` for the exact class contract. Do not use ad hoc inline CSS.

## HTMX Fragment Patterns

Preferred patterns:
- partial replacement of the smallest meaningful content unit
- explicit `hx-target` and `hx-swap` on every interactive element
- filters as HTML form inputs (let browser serialize query state)
- `hx-push-url` for URL-addressable filter state (where appropriate)
- chart panel + summary card updated together via OOB swap
- side panels and detail drawers as separate fragment endpoints
- server-rendered fallback for every HTMX-enhanced fragment

Anti-patterns:
- replacing the full content area on every filter interaction
- client-side data reshaping (backend must own all aggregation)
- ad hoc JavaScript state alongside HTMX (fragile, opaque)
- charts with spinners that do not reflect filter state
- OOB swaps that update unrelated UI regions in one response

## What This Doctrine Does NOT Cover
- Data acquisition, ingestion, and storage pipelines.
- Authentication, authorization, and row-level security.
- Deployment and hosting of Plotly.js assets (assumed CDN or local static file).
- Non-analytics visualization (e.g., node-graph network topologies outside Plotly's scope).