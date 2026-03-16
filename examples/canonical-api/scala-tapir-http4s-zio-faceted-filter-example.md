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

- `filterRows(state)` — `filter { row => matchesDim(...) }` per dimension.
- `facetCounts(state, dim)` — `dim match { ... }` dispatch; relaxes _in, keeps _out for
  target; applies all other dimensions fully. Returns `Map[String, Int]`.
- `excludeImpactCounts(state, dim)` — per option: other dims fully; target _out minus
  current option; _in ignored.

## Multi-value parameter parsing

http4s `req.multiParams.getOrElse("status_out", Nil)` returns `List[String]` with all
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
- `examples/canonical-api/scala-tapir-http4s-zio-faceted-filter-example.scala`
