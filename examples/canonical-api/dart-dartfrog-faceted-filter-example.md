# Dart Dart Frog Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Dart and Dart Frog.
HTML is rendered server-side using `StringBuffer`. The filter pipeline uses Dart's type
system with `class` definitions and typed `Map`/`List` objects.

## Language and rendering idiom

Single `.dart` file. `ReportRow` is a `const` class. `QueryState` is a class with
`List<String>` fields. HTML is built with `StringBuffer` and `buf.write(...)` calls.

`normalize` uses a `Set<String>` for deduplication, then `.sort()` on the resulting list.

## Filter logic

- `filterRows(state)` — `.where((row) => matchesDim(...))` per dimension.
- `facetCounts(state, dim)` — `switch (dim)` dispatch; relaxes _in, keeps _out for target;
  applies all other dimensions fully. Returns `Map<String, int>`.
- `excludeImpactCounts(state, dim)` — per option: other dims fully; target _out minus
  current option; _in ignored.

## Multi-value parameter parsing

`context.request.uri.queryParametersAll["status_out"]` returns `List<String>?` with all
values for repeated keys. `normalize` handles null and deduplicates and sorts.

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
- `examples/canonical-api/dart-dartfrog-faceted-filter-example.dart`
