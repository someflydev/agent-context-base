# Nim Jester Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Nim and Jester.
HTML is rendered server-side using `fmt` strings and `&` concatenation. The filter pipeline
uses Nim's `object` types and `Table[string, int]` for count maps.

## Language and rendering idiom

Single `.nim` file. `ReportRow` is a named tuple. `QueryState` is an `object`. HTML is
assembled via `fmt"""..."""` string interpolation and `&=` concatenation on a `string`
result variable. `capFirst` provides title-case for display labels.

`normalize` uses `initHashSet[string]()` for deduplication, then `result.sort()`.

## Filter logic

- `filterRows` — `for row in reportRows` with `matchesDim` per dimension.
- `facetCounts` — `if/elif` dispatch on dimension name; relaxes _in, keeps _out for target;
  applies all other dimensions fully. Returns `Table[string, int]`.
- `excludeImpactCounts` — per option: other dims fully; target _out minus current option;
  _in ignored.

## Multi-value parameter parsing

Jester's `@"status_out"` returns only the last value for repeated params. This example
parses multi-value params by splitting `request.url.query` on `'&'` and extracting all
matching key-value pairs. `decodeUrl()` handles percent-encoding.

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
- `examples/canonical-api/nim-jester-happyx-faceted-filter-example.nim`
