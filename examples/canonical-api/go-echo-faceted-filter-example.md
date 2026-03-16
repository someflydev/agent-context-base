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

- `filterRows(state)` — include/exclude per dimension using `slices.Contains`.
- `facetCounts(state, dim)` — relaxes _in, keeps _out for target dimension; full filtering
  on all other dimensions.
- `excludeImpactCounts(state, dim)` — applies all other dimensions fully; applies target
  dimension's _out except the current option; ignores _in.

`normalize` uses a `map[string]struct{}` seen-set then sorts with `slices.Sort`.

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

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/go-echo-faceted-filter-example.go`
- `examples/canonical-api/go-echo-faceted-filter-panel-template.templ`
