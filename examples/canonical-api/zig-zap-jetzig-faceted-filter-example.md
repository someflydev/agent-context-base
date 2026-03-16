# Zig Jetzig/Zap Faceted Filter Example

## Purpose

Demonstrates the split include/exclude filter panel pattern using Zig and Jetzig (Zap).
The handler computes all counts and passes them to a Zmpl template via Jetzig's data
object. The template renders the complete filter panel HTML.

## Language and rendering idiom

Single `.zig` handler file paired with a `.zmpl` template. Zig's type system drives the
data layer: `ReportRow` is a `struct`, `QueryState` holds `[]const u8` fields.

HTML is rendered by `zig-zap-jetzig-faceted-filter-panel-template.zmpl` using `{{variable}}`
interpolation. All count values are pre-computed in the handler and passed to the template
via `data.put(...)`.

`comptime dim` parameter on `countFacet` and `countExcludeImpact` uses `@field(row, dim)`
for zero-overhead dimension dispatch.

**Note:** This example uses single-string filter state for simplicity. A production
implementation would use `ArrayList([]const u8)` per filter field with a proper
query-string parser, as multi-value params (`?status_out=archived&status_out=paused`) are
limited in early Jetzig/Zap versions.

## Filter logic

- `countFilteredRows(state)` — applies all three dimensions with `matchesDimSingle`.
- `countFacet(state, dim, option)` — relaxes _in, keeps _out for target dimension; applies
  all other dimensions fully.
- `countExcludeImpact(state, dim, option)` — applies all other dimensions fully; no D_in;
  counts rows where `row[dim] == option`.

## Multi-value parameter parsing

`request.queryParam(key)` returns the first value for a key. This example uses single-value
state per field. Multi-value support requires manual query string parsing or a future
Jetzig/Zap API that returns all values for a key.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: result count and results list |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

The template expects these data keys to be populated by the handler:

Include counts: `team_growth_count`, `team_platform_count`, `status_active_count`,
`status_paused_inc_count`, `status_archived_inc_count`, `region_us_count`, `region_eu_count`,
`region_apac_count`.

Exclude impacts: `team_growth_impact`, `team_platform_impact`, `status_active_impact`,
`paused_impact`, `archived_impact`, `region_us_impact`, `region_eu_impact`,
`region_apac_impact`.

Quick exclude state: `archived_active`, `paused_active` (boolean).

All option `<label>` elements carry `data-filter-dimension`, `data-filter-option`,
`data-filter-mode`, `data-option-count`. Quick exclude labels carry `data-role="quick-exclude"`,
`data-quick-exclude-dimension`, `data-quick-exclude-value`, `data-active`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/zig-zap-jetzig-faceted-filter-example.zig`
- `examples/canonical-api/zig-zap-jetzig-faceted-filter-panel-template.zmpl`
