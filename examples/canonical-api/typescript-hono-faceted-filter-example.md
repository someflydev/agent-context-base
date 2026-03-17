# TypeScript Hono Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using TypeScript and Hono
running on Bun. HTML is rendered server-side using template literal string building. The
entire filter pipeline is implemented as typed functions over a `QueryState` type.

## Language and rendering idiom

Single `.ts` file targeting Bun runtime. HTML is assembled via nested template literals
(`\`...\``) with `${...}` interpolation. Array `join('')` flattens per-option label arrays.

TypeScript interfaces `ReportRow` and `QueryState` enforce the data model. All filter
functions are typed and pure — no side effects or mutable state outside the route handlers.

## Filter logic

- `filterRows(state)` — calls `applyTextSearch` first, then `Array.filter` over the result;
  `matchesDim` applies include and exclude lists per dimension.
- `facetCounts(state, dim)` — calls `applyTextSearch` first (Q is never relaxed); per-dimension
  switch relaxes _in, keeps _out for target; applies all other dimensions fully.
- `excludeImpactCounts(state, dim)` — calls `applyTextSearch` first; per option: other dims
  fully applied; target _out minus current option applied; _in ignored.
- `applyTextSearch(rows, q)` — filters rows by case-insensitive substring match on `report_id`;
  returns all rows when `q` is empty.
- `sortRows(rows, sortVal)` — returns a sorted copy; `events_desc` descending by events then
  `report_id` asc; `events_asc` ascending by events then `report_id` asc; `name_asc` by
  `report_id` ascending.

`normalize` uses `Set` for dedup then `.sort()`. `normalizeSort` validates against
`VALID_SORT_VALUES`, falling back to `"events_desc"`.

## Multi-value parameter parsing

`new URL(c.req.url).searchParams.getAll("status_out")` returns `string[]` with all values
for repeated keys. `normalize` deduplicates and sorts.

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
- `examples/canonical-api/typescript-hono-faceted-filter-example.ts`
