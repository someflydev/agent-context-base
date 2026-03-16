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

- `filterRows(state)` — `Array.filter` over `reportRows`; `matchesDim` applies include and
  exclude lists per dimension.
- `facetCounts(state, dim)` — per-dimension switch relaxes _in, keeps _out for target;
  applies all other dimensions fully.
- `excludeImpactCounts(state, dim)` — per option: other dims fully applied; target _out
  minus current option applied; _in ignored.

`normalize` uses `Set` for dedup then `.sort()`.

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

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/typescript-hono-faceted-filter-example.ts`
