# Crystal Kemal Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Crystal and Kemal.
HTML is rendered server-side using `String.build { |io| io << ... }`. The filter pipeline
uses Crystal's static typing with `record` structs and typed `Hash` objects.

## Language and rendering idiom

Single `.cr` file. `ReportRow` is a Crystal `record`. `QueryState` is a class with
`Array(String)` and `String` fields. HTML is built with `String.build { |io| io << ... }` for
efficient concatenation.

`normalize` uses `.uniq.sort` after `.strip.downcase` on each element.

## Filter logic

- `filter_rows(state)` — calls `apply_text_search` first, then `select { |row| matches_dim?(...) }`
  per dimension, then `sort_rows`.
- `facet_counts(state, dim)` — calls `apply_text_search` first; `case dim` dispatch; relaxes
  _in, keeps _out for target; applies all other dimensions fully.
  Returns `Hash(String, Int32)`. Sort is never applied.
- `exclude_impact_counts(state, dim)` — calls `apply_text_search` first; per option: other
  dims fully; target _out minus current option; _in ignored. Sort is never applied.
- `apply_text_search(rows, query)` — selects rows where `report_id.downcase.includes?(query)`.
  Returns all rows if query is empty.
- `sort_rows(rows, sort_value)` — `"events_asc"`: ascending events tiebreak report_id;
  `"name_asc"`: ascending report_id; default `"events_desc"`: descending events tiebreak report_id.
- `normalize_sort(s)` — validates against allowed values; defaults to `"events_desc"`.

## QueryState

8 fields: `team_in`, `team_out`, `status_in`, `status_out`, `region_in`, `region_out` (all
`Array(String)`), `query : String = ""`, `sort : String = "events_desc"`. Implemented as a
Crystal class with `property` accessors. Query is normalized to `.strip.downcase` at parse
time; sort is validated against allowed values via `normalize_sort`.

## Rendering additions

Search input at the top of the filter panel:
`name="query"`, `data-role="search-input"`, `data-search-query="{query}"`,
`hx-get="/ui/reports/filter-panel"`, `hx-target="#filter-panel"`,
`hx-include="#report-filters"`, `hx-trigger="keyup changed delay:300ms"`.

Sort select below the result-count badge in the results section:
`name="sort"`, `data-role="sort-select"`, `data-sort-order="{sort}"`,
`hx-get="/ui/reports/results"`, `hx-target="#report-results"`, `hx-include="#report-filters"`.
Options use a `sel()` helper that returns `" selected"` when value matches `state.sort`.

Full-page layout uses independent scroll: `data-role="reports-layout"` wrapper with
`class="flex h-screen overflow-hidden"`; filter aside with `overflow-y-auto`; results main
with `overflow-y-auto`. The layout wrapper is NOT a partial swap target.

## Multi-value parameter parsing

Kemal `env.request.query_params.fetch_all("status_out")` returns `Array(String)` with all
values for repeated keys. `normalize` deduplicates and sorts.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: OOB result-count badge + sort select + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

All option elements carry `data-filter-dimension`, `data-filter-option`, `data-filter-mode`,
`data-option-count`. Include options for excluded values: `data-excluded="true"`, count=0,
`disabled`. Exclude options for active values: `data-active="true"`, red styling.

Quick exclude labels carry `data-role="quick-exclude"`, `data-quick-exclude-dimension`,
`data-quick-exclude-value`, `data-active`.

Search input: `data-role="search-input"`, `data-search-query="{query}"`.

Sort select: `data-role="sort-select"`, `data-sort-order="{sort}"`. Options pre-select
the current sort value using `sort_value == state.sort ? " selected" : ""`.

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`,
`data-search-query="{query}"`, `data-sort-order="{sort}"`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

Full page layout uses independent scroll:
`data-role="reports-layout"`, `id="reports-layout"`, `class="flex h-screen overflow-hidden"`.
Filter aside: `id="filter-panel"`, `class="w-72 flex-shrink-0 overflow-y-auto border-r p-4"`.
Results main: `id="report-results-container"`, `class="flex-1 overflow-y-auto p-4"`.

Fingerprint format: `team_in=...|...|region_out=...|query={q}|sort={sort}`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/crystal-kemal-avram-faceted-filter-example.cr`
