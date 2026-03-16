# Crystal Kemal Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Crystal and Kemal.
HTML is rendered server-side using `String.build { |io| io << ... }`. The filter pipeline
uses Crystal's static typing with `record` structs and typed `Hash` objects.

## Language and rendering idiom

Single `.cr` file. `ReportRow` is a Crystal `record`. `QueryState` is a class with
`Array(String)` fields. HTML is built with `String.build { |io| io << ... }` for
efficient concatenation.

`normalize` uses `.uniq.sort` after `.strip.downcase` on each element.

## Filter logic

- `filter_rows(state)` — `select { |row| matches_dim(...) }` per dimension.
- `facet_counts(state, dim)` — `case dim` dispatch; relaxes _in, keeps _out for target;
  applies all other dimensions fully. Returns `Hash(String, Int32)`.
- `exclude_impact_counts(state, dim)` — per option: other dims fully; target _out minus
  current option; _in ignored.

## Multi-value parameter parsing

Kemal `env.request.query_params.fetch_all("status_out")` returns `Array(String)` with all
values for repeated keys. `normalize` deduplicates and sorts.

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
- `examples/canonical-api/crystal-kemal-avram-faceted-filter-example.cr`
