# Analytics Workbench

## Use This Archetype When
- repo delivers operational or product analytics views over internal or derived data
- charts, filters, drilldowns, and summary cards are the primary UI surface
- a server-rendered backend owns aggregation, figure construction, and HTML fragments
- HTMX updates chart panels and filter-results sections without a frontend framework
- Tailwind provides interactive filter UI state expression
- cross-stack comparison or multi-language parity is in scope

## Typical Repo Surface
- routes/handlers for pages, chart data endpoints, and HTMX partials
- figure-builder modules (separate from route handlers)
- aggregation/query service modules (separate from figure builders)
- template files (Jinja2 / templ / Askama / HEEx) for pages and partials
- static assets: Tailwind (CDN or compiled), HTMX (CDN or bundled), Plotly.js (CDN)
- seed data generators (dogfooding canonical-faker domain and helpers)
- unit tests for aggregation logic and figure-builder output
- smoke tests for route availability and chart data shape
- integration tests for filter-to-chart query state alignment

## Required Doctrine
- context/doctrine/plotly-htmx-server-rendered-viz.md
- context/doctrine/tailwind-utility-first.md
- context/doctrine/backend-driven-ui-correctness.md
- context/doctrine/filter-state-and-query-state.md
- context/doctrine/filter-panel-rendering-rules.md

## Common Workflows
- context/workflows/add-visualization-panel.md
- context/workflows/add-plotly-backed-query-view.md
- context/workflows/add-faceted-filter-ui.md
- context/workflows/add-seed-data.md
- context/workflows/add-smoke-tests.md

## Common Stack Packs
- context/stacks/python-fastapi-jinja2-htmx-plotly.md
- context/stacks/go-echo-templ-htmx-plotly.md
- context/stacks/rust-axum-askama-htmx-plotly.md
- context/stacks/elixir-phoenix-htmx-plotly.md
- context/stacks/backend-driven-ui-htmx-tailwind-plotly.md

## Likely Examples
- examples/canonical-analytics/CATALOG.md

## Typical Anti-Patterns
- chart endpoints that do not respect the same filter state as result routes
- figure construction inside route handlers instead of dedicated builders
- shipping row-level datasets to the browser and aggregating in JavaScript
- one monolithic "everything dashboard" with no information hierarchy
- omitting paired textual summaries alongside charts
- building bespoke seed data instead of dogfooding the canonical-faker domain