# Go Echo Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Go and the Echo
web framework. HTML is rendered server-side using `strings.Builder`. A companion templ
component file shows the idiomatic typed-template approach.

## Language and rendering idiom

Single `package main` file. HTML is assembled via `strings.Builder` with `WriteString`
calls and `fmt.Sprintf` for attribute interpolation. The `renderFilterPanel` function
iterates over a fixed dimension list and calls helper functions per dimension.

`go-echo-faceted-filter-panel-template.templ` provides the idiomatic Go templ equivalent:
typed `templ` components with `templ.Classes()` for conditional class lists and explicit
conditional `data-excluded`/`data-active` attribute emission.

## Filter logic

- `filterRows(state)` — calls `applyTextSearch` first, then applies include/exclude per
  dimension using `contains`.
- `facetCounts(state, dim)` — calls `applyTextSearch` first (Q is never relaxed); relaxes
  _in, keeps _out for target dimension; full filtering on all other dimensions.
- `excludeImpactCounts(state, dim)` — calls `applyTextSearch` first; applies all other
  dimensions fully; applies target dimension's _out except the current option; ignores _in.
- `applyTextSearch(rows, q)` — filters rows by `strings.Contains(strings.ToLower(row.ReportID), q)`;
  returns input slice unchanged when q is empty.
- `sortRows(rows, sortVal)` — sorts a copy of the slice using `sort.Slice`: `events_desc`
  (descending events, tiebreak ReportID asc), `events_asc` (ascending events, tiebreak
  ReportID asc), `name_asc` (ascending ReportID). Sort never affects counts.

`normalize` uses a `map[string]bool` seen-set then sorts with `sort.Strings`.

## Multi-value parameter parsing

`c.QueryParams()["status_out"]` returns `[]string` with all values for repeated keys.
`normalize` deduplicates and sorts the slice.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: OOB result-count badge + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

All option elements carry `data-filter-dimension`, `data-filter-option`, `data-filter-mode`,
`data-option-count`. Include options for excluded values add `data-excluded="true"`, count=0,
`disabled`. Exclude options for active values add `data-active="true"` and red styling.

Quick exclude labels carry `data-role="quick-exclude"`, `data-quick-exclude-dimension`,
`data-quick-exclude-value`, `data-active`.

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

**Search input** (at top of filter panel, above quick-excludes strip):
- `name="query"` — submitted with form; normalized to trimmed lowercase via `strings.TrimSpace(strings.ToLower(...))`
- `data-role="search-input"` — identifies the search input element
- `data-search-query="{Q}"` — reflects current query value for client reads

**Sort select** (in results section, below result-count badge, above result cards):
- `name="sort"` — submitted with form; valid values: `events_desc`, `events_asc`, `name_asc`
- `data-role="sort-select"` — identifies the sort control element
- `data-sort-order="{sort}"` — reflects current sort value; `selected` attribute set on
  matching option via `selectedAttr` helper to prevent dropdown reset on HTMX swaps

**Results section** (`id="report-results"`) additional attributes:
- `data-search-query="{Q}"` — current text search query
- `data-sort-order="{sort}"` — current sort order

**Layout wrapper** (`id="reports-layout"`):
- `data-role="reports-layout"` — identifies the independent scroll layout container
- Structure: `<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">`
  with `<aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">`
  and `<main id="report-results-container" class="flex-1 overflow-y-auto p-4">`

**State fields** `Query string` and `Sort string` are now part of `QueryState` (8 fields total).
Both are included in the fingerprint as `|query=%s|sort=%s` at the end of the format string.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/go-echo-faceted-filter-example.go`
- `examples/canonical-api/go-echo-faceted-filter-panel-template.templ`
