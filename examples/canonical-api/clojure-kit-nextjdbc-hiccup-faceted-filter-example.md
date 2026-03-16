# Clojure Kit/Hiccup Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Clojure and Kit
with Hiccup HTML generation. The filter pipeline is implemented as pure Clojure functions
over a map-based `QueryState`. Hiccup vectors represent the HTML tree.

## Language and rendering idiom

Single `.clj` namespace file. HTML is built with Hiccup2 (`hiccup2.core/html`) using
nested Clojure vectors: `[:div {:data-filter-dimension dim} [...]]`. Keyword data-*
attributes (`:data-filter-dimension`) are used throughout.

`QueryState` is a plain Clojure map with six keys. `normalize` uses `(distinct)`,
`(map str/lower-case)`, `(map str/trim)`, and `(sort)` in a threading macro.
All filter functions are pure — no side effects.

## Filter logic

- `filter-rows` — `(filter ...)` with `matches-dim` per dimension.
- `facet-counts` — per-dimension `cond` dispatch; relaxes `:_in`, keeps `:_out` for
  target; applies all other dimensions fully. Returns frequency map.
- `exclude-impact-counts` — per option: other dims fully applied; target `:_out` minus
  current option; `:_in` ignored. Returns count map.

## Multi-value parameter parsing

Kit (Reitit + Ring) query params: `(get-in request [:query-params "status_out"])` may
return a string or vector. `normalize` coerces with `(if (string? v) [v] (or v []))` before
dedup and sort.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: OOB result-count badge + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

All option elements carry `data-filter-dimension`, `data-filter-option`, `data-filter-mode`,
`data-option-count`. Include options for excluded values: `data-excluded "true"`, count=0,
`disabled true`. Exclude options for active values: `data-active "true"`, red styling.

Quick exclude labels carry `data-role="quick-exclude"`, `data-quick-exclude-dimension`,
`data-quick-exclude-value`, `data-active`.

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-faceted-filter-example.clj`
