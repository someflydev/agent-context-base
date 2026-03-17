# Scala http4s/ZIO Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Scala 3 with http4s
and ZIO. HTML is rendered server-side using `s"""..."""` multiline string interpolation.
The filter pipeline uses functional style with immutable case classes.

## Language and rendering idiom

Single Scala 3 `object` file with `case class QueryState` and `case class ReportRow`.
HTML is assembled via `s"""..."""` string interpolation and `.mkString` for joining
per-option HTML strings. All filter functions are pure.

`normalize` uses `toSet.toList.sorted` for deduplication and sorting, with `.trim.toLowerCase`.

## Filter logic

- `filterRows(state)` — calls `applyTextSearch` first, then `filter { row => matchesDim(...) }`
  per dimension, then `sortRows`.
- `facetCounts(state, dim)` — calls `applyTextSearch` first; `dim match { ... }` dispatch;
  relaxes _in, keeps _out for target; applies all other dimensions fully.
  Returns `Map[String, Int]`. Sort is never applied.
- `excludeImpactCounts(state, dim)` — calls `applyTextSearch` first; per option: other dims
  fully; target _out minus current option; _in ignored. Sort is never applied.
- `applyTextSearch(rows, q)` — filters on `reportId.toLowerCase.contains(q)`. Returns all
  rows if q is empty.
- `sortRows(rows, sortVal)` — `"events_asc"`: ascending events tiebreak reportId;
  `"name_asc"`: ascending reportId; default `"events_desc"`: descending events tiebreak reportId.
- `normalizeSort(s)` — validates against allowed values; defaults to `"events_desc"`.

## Multi-value parameter parsing

http4s `req.multiParams.getOrElse("status_out", Nil)` returns `List[String]` with all
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
the current sort value using `if (state.sort == val) " selected" else ""`.

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
- `examples/canonical-api/scala-tapir-http4s-zio-faceted-filter-example.scala`
