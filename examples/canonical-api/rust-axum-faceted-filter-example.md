# Rust Axum Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Rust and Axum.
HTML is rendered server-side via `String::push_str`. The filter pipeline is implemented as
pure functions over an immutable `QueryState` struct.

## Language and rendering idiom

Single `main.rs`-style file. HTML is assembled with `String::push_str` and `format!` macro
calls. All filter functions take `&QueryState` and return owned values.

Serde `#[derive(Deserialize)]` on `FilterQuery` with `#[serde(default)]` on each
`Vec<String>` field handles missing query params gracefully. `normalize` uses `BTreeSet`
for automatic sorting and deduplication, then collects to `Vec<String>`.

## Filter logic

- `filter_rows(state)` — calls `apply_text_search` first, then `iter().filter()` with
  `matches_dim` per dimension over the result.
- `facet_counts(state, dim)` — calls `apply_text_search` first (Q is never relaxed);
  string-matched dimension dispatch; relaxes _in, keeps _out for target dimension; applies
  all other dimensions fully.
- `exclude_impact_counts(state, dim)` — calls `apply_text_search` first; per option: other
  dims fully applied; target _out minus current option; _in ignored.
- `apply_text_search<'a>(rows, q)` — returns `Vec<&'a ReportRow>` filtered by
  `report_id.to_lowercase().contains(q)`; returns all rows when `q` is empty.
- `sort_rows(rows, sort_val)` — sorts in place using `sort_by`; `events_desc` descending by
  events then `report_id` asc; `events_asc` ascending by events then `report_id` asc;
  `name_asc` by `report_id` ascending.

## Multi-value parameter parsing

Axum's `Query<FilterQuery>` with `Vec<String>` fields handles repeated query params
(`?status_out=archived&status_out=paused`) natively via serde. `normalize` deduplicates
and sorts.

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
Options pre-selected by comparing value against current `state.sort`. Fires HTMX GET including
`#report-filters`.

Layout wrapper: `data-role="reports-layout"`, `id="reports-layout"`, `class="flex h-screen overflow-hidden"`.
Filter aside: `id="filter-panel"`, `class="w-72 flex-shrink-0 overflow-y-auto border-r p-4"`.
Results main: `id="report-results-container"`, `class="flex-1 overflow-y-auto p-4"`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/rust-axum-faceted-filter-example.rs`
