# Nim Jester Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Nim and Jester.
HTML is rendered server-side using `fmt` strings and `&` concatenation. The filter pipeline
uses Nim's `object` types and `Table[string, int]` for count maps.

## Language and rendering idiom

Single `.nim` file. `ReportRow` is a named tuple. `QueryState` is an `object` with
`teamIn`, `teamOut`, `statusIn`, `statusOut`, `regionIn`, `regionOut` seq fields plus
`query: string` and `sort: string`. HTML is assembled via `fmt"""..."""` string
interpolation and `&=` concatenation on a `string` result variable. `capFirst` provides
title-case for display labels.

`normalize` uses `initHashSet[string]()` for deduplication, then `result.sort()`.
`normalizeSort` validates against the three allowed sort values.

## Filter logic

- `applyTextSearch(rows, q)` — `filterIt` with `it.reportId.toLowerAscii().contains(q.toLowerAscii())`
  substring check; returns all rows when `q` is empty. Called first in all three filter
  functions.
- `filterRows` — calls `applyTextSearch` first, then `for row in searched` with `matchesDim`
  per dimension, then `sortRows`.
- `facetCounts` — calls `applyTextSearch` first; `case dimension` dispatch; relaxes _in,
  keeps _out for target; applies all other dimensions fully. Returns `Table[string, int]`.
  Sort never affects counts.
- `excludeImpactCounts` — calls `applyTextSearch` first; per option: other dims fully;
  target _out minus current option; _in ignored.
- `sortRows(rows, sortVal)` — sorts a copy using `algorithm.sort` with a `cmp` proc
  dispatched on `sortVal`: `events_desc` (default), `events_asc`, `name_asc`; event sorts
  tiebreak by `reportId`.

## Multi-value parameter parsing

Jester's `@"status_out"` returns only the last value for repeated params. This example
parses multi-value params by splitting `request.url.query` on `'&'` and extracting all
matching key-value pairs. `decodeUrl()` handles percent-encoding.

Single-value params `query` and `sort` use `parseSingleParam` which returns the first
match or a supplied default.

## Rendering additions

**Search input** — rendered at top of filter panel via `fmt"""<input ... />"""` with
`hx-trigger="keyup changed delay:300ms"`.

**Sort select** — `renderSortSelect(state)` builds HTML with conditional `selected`
attributes using `if state.sort == val: " selected" else: ""`.

**Independent scroll layout** — full page uses
`<div data-role="reports-layout" class="flex h-screen overflow-hidden">` with
`<aside class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">` and
`<main class="flex-1 overflow-y-auto p-4">`.

**Results section** carries `data-search-query` and `data-sort-order` attributes.

## Fingerprint

`"|query=" & state.query & "|sort=" & state.sort` appended at the end of the fingerprint
string.

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

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`,
`data-search-query`, `data-sort-order`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.
Search input: `data-role="search-input"`, `data-search-query`.
Sort select: `data-role="sort-select"`, `data-sort-order`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/nim-jester-happyx-faceted-filter-example.nim`
