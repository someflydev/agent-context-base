# Dart Dart Frog Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Dart and Dart Frog.
HTML is rendered server-side using `StringBuffer`. The filter pipeline uses Dart's type
system with `class` definitions and typed `Map`/`List` objects.

## Language and rendering idiom

Single `.dart` file. `ReportRow` is a `const` class. `QueryState` is a class with
`List<String>` fields plus `String query` and `String sort`. HTML is built with
`StringBuffer` and `buf.write(...)` calls.

`normalize` uses a `Set<String>` for deduplication, then `.sort()` on the resulting list.
`normalizeSort` validates against the three allowed sort values.

## Filter logic

- `applyTextSearch(rows, q)` — filters rows by case-insensitive substring match on
  `reportId`; returns all rows when `q` is empty. Called first in all three filter functions.
- `filterRows(state)` — calls `applyTextSearch` first, then `.where((row) => matchesDim(...))`
  per dimension, then `sortRows`.
- `facetCounts(state, dim)` — calls `applyTextSearch` first; `switch (dim)` dispatch;
  relaxes _in, keeps _out for target; applies all other dimensions fully. Returns
  `Map<String, int>`. Sort never affects counts.
- `excludeImpactCounts(state, dim)` — calls `applyTextSearch` first; per option: other dims
  fully; target _out minus current option; _in ignored.
- `sortRows(rows, sortVal)` — sorts a copy by `events_desc` (default), `events_asc`, or
  `name_asc`; tiebreaks on `reportId` ascending for event-based sorts.

## Multi-value parameter parsing

`context.request.uri.queryParametersAll["status_out"]` returns `List<String>?` with all
values for repeated keys. `normalize` handles null and deduplicates and sorts.

Single-value params `query` and `sort` use `uri.queryParameters[key] ?? default`.

## Rendering additions

**Search input** — at top of filter panel; uses `hx-trigger="keyup changed delay:300ms"`.

**Sort select** — in results section; `data-sort-order` attribute; conditional `selected`
via `state.sort == val ? ' selected' : ''`.

**Independent scroll layout** — full page uses
`<div data-role="reports-layout" class="flex h-screen overflow-hidden">` with
`<aside class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">` and
`<main class="flex-1 overflow-y-auto p-4">`.

**Results section** carries `data-search-query` and `data-sort-order` attributes.

## Fingerprint

`|query={Q}|sort={sort}` appended at the end of the fingerprint string.

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
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/dart-dartfrog-faceted-filter-example.dart`
