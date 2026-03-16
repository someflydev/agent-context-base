# Kotlin http4k Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Kotlin and http4k.
HTML is rendered server-side using `buildString { append(...) }`. The filter pipeline is
implemented as top-level functions over a `QueryState` data class.

## Language and rendering idiom

Single Kotlin file with `data class QueryState` and `data class ReportRow`. HTML is assembled
via `buildString { append(...) }` with string templates (`${...}`) for interpolation.
Per-option lists are built with `joinToString("")`.

`normalize` uses `toSortedSet()` for automatic deduplication and sorting, then `toList()`.

## Filter logic

- `filterRows(state)` — `filter { matchesDim(...) }` per dimension.
- `facetCounts(state, dim)` — `when (dim)` dispatch; relaxes _in, keeps _out for target;
  applies all other dimensions fully.
- `excludeImpactCounts(state, dim)` — per option: other dims fully; target _out minus
  current option; _in ignored.

## Multi-value parameter parsing

http4k `request.queries("status_out")` returns `List<String?>`. `normalize` filters nulls,
trims, lowercases, deduplicates, and sorts.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: OOB result-count badge + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

All option elements carry `data-filter-dimension`, `data-filter-option`, `data-filter-mode`,
`data-option-count`. Include options for excluded values: `data-excluded="true"`, count=0,
`disabled`. Exclude options for active values: `data-active="true"`, red styling.

Quick exclude labels carry `data-role="quick-exclude"`, `data-quick-exclude-dimension`,
`data-quick-exclude-value`, `data-active`.

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/kotlin-http4k-exposed-faceted-filter-example.kt`
