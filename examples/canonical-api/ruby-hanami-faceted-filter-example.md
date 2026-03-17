# Ruby Hanami Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Ruby and Hanami.
HTML is rendered server-side using `<<~HTML` heredoc interpolation inside a `FilterService`
module. The example follows Hanami's action-based architecture with a shared service layer.

## Language and rendering idiom

Single `.rb` file with `FilterService` module and `Hanami::Action` subclasses. HTML is
assembled via `<<~HTML` heredocs with `#{}` string interpolation. `Array.join` flattens
per-option HTML strings.

`QueryState` is a Ruby `Struct` with eight fields (six `Array` fields, plus `query` String
and `sort` String). `normalize` uses `uniq` and `sort` after `strip.downcase`. The
`FilterService` module contains all pure filter functions as module methods.

## Filter logic

- `filter_rows(state)` — calls `apply_text_search` first, then `select` with `matches_dim?`
  per dimension over the result.
- `facet_counts(state, dim)` — calls `apply_text_search` first (Q is never relaxed);
  per-dimension case dispatch; relaxes _in, keeps _out for target; applies all other
  dimensions fully.
- `exclude_impact_counts(state, dim)` — calls `apply_text_search` first; per option: other
  dims fully; target _out minus current option; _in ignored.
- `apply_text_search(rows, query)` — `rows.select { |r| r[:report_id].downcase.include?(query) }`;
  returns all rows when `query` is empty.
- `sort_rows(rows, sort_value)` — `case sort_value` dispatch; `events_asc` sort by
  `[events, report_id]`; `name_asc` sort by `report_id`; default `events_desc` sort by
  `[-events, report_id]`.

## Multi-value parameter parsing

Hanami/Rack `params[:status_out]` may return a `String` or `Array` depending on the
request. `normalize` wraps non-array values with `Array()` before dedup and sort.

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
`data-search-query` (current normalized query string), `data-sort-order` (current sort value).

OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

Search input: `data-role="search-input"`, `data-search-query` (current query value), `name="query"`.
Fires HTMX GET on `keyup changed delay:300ms` including `#report-filters`.

Sort select: `data-role="sort-select"`, `data-sort-order` (current sort value), `name="sort"`.
Options pre-selected by comparing value against `state.sort`. Fires HTMX GET including
`#report-filters`.

Layout wrapper: `data-role="reports-layout"`, `id="reports-layout"`, `class="flex h-screen overflow-hidden"`.
Filter aside: `id="filter-panel"`, `class="w-72 flex-shrink-0 overflow-y-auto border-r p-4"`.
Results main: `id="report-results-container"`, `class="flex-1 overflow-y-auto p-4"`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/ruby-hanami-faceted-filter-example.rb`
