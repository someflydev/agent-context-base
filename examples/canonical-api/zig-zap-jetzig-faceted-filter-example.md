# Zig Jetzig/Zap Faceted Filter Example

## Purpose

Demonstrates the split include/exclude filter panel pattern using Zig and Jetzig (Zap),
extended with PROMPT_64 features: text search (RULE 4), sort order (RULE 5), and
independent scroll layout (RULE 6).

The handler computes all counts and passes them to a Zmpl template via Jetzig's data
object. The template renders the complete filter panel and results layout HTML.

## Language and rendering idiom

Single `.zig` handler file paired with a `.zmpl` template. Zig's type system drives the
data layer: `ReportRow` is a `struct`, `QueryState` holds `[]const u8` fields including
`query` and `sort`.

HTML is rendered by `zig-zap-jetzig-faceted-filter-panel-template.zmpl` using `{{variable}}`
interpolation and Zmpl conditional syntax (`@if (condition) { selected }`). All count
values are pre-computed in the handler and passed to the template via `data.put(...)`.

`comptime dim` parameter on `countFacet` and `countExcludeImpact` uses `@field(row, dim)`
for zero-overhead dimension dispatch.

**Note:** This example uses single-string filter state for simplicity. A production
implementation would use `ArrayList([]const u8)` per filter field with a proper
query-string parser, as multi-value params (`?status_out=archived&status_out=paused`) are
limited in early Jetzig/Zap versions.

## QueryState (8 fields)

```zig
const QueryState = struct {
    team_in:    []const u8 = "",
    team_out:   []const u8 = "",
    status_in:  []const u8 = "",
    status_out: []const u8 = "",
    region_in:  []const u8 = "",
    region_out: []const u8 = "",
    query:      []const u8 = "",            // RULE 4: text search
    sort:       []const u8 = "events_desc", // RULE 5: sort order
};
```

`query` is parsed from the `query` param as-is. `sort` is validated via `normalizeSort`
against the three allowed values (`events_desc`, `events_asc`, `name_asc`); any unrecognized
value falls back to `"events_desc"`.

## Text search — `applyTextSearch` (RULE 4)

```zig
fn applyTextSearch(
    allocator: std.mem.Allocator,
    rows: []const ReportRow,
    q: []const u8,
) ![]ReportRow
```

Returns an owned slice that the caller must `defer allocator.free(...)`. When `q` is empty,
returns a full `@memcpy` copy of the input. When non-empty, filters rows where
`row.report_id` contains `q` as a case-insensitive substring via the inline
`containsIgnoreCase` helper (ASCII lowercasing with `asciiToLower`, no per-character heap
allocation). Uses `std.ArrayList(ReportRow)` to collect matches and returns
`list.toOwnedSlice()`.

RULE 4b: `applyTextSearch` is called first in all three count helpers
(`countFilteredRows`, `countFacet`, `countExcludeImpact`). Q is never relaxed in any path.

## Sort — `sortRows` (RULE 5)

```zig
fn sortRows(
    allocator: std.mem.Allocator,
    rows: []const ReportRow,
    sort_val: []const u8,
) ![]ReportRow
```

Returns a new owned slice (caller frees). Copies the input with `@memcpy` then sorts in
place using `std.sort.block` with a `SortContext` struct that carries `sort_val` and
implements `lessThan`.

Sort semantics:
- `"events_asc"` — ascending by events, tiebreak by report_id ascending.
- `"name_asc"` — lexicographic ascending by report_id.
- default (`"events_desc"`) — descending by events, tiebreak by report_id ascending.

Sort is applied only when building the result list; it never affects any counts.

## Filter logic

1. `applyTextSearch(allocator, &report_rows, state.query)` — base filter, Q never relaxed.
2. Dimension filters via `matchesDimSingle` — single-value include/exclude per field.
3. `sortRows(allocator, filtered_list.items, state.sort)` — applied to result list only.

Count helpers:
- `countFilteredRows` — text search then all three dimensions with `matchesDimSingle`.
- `countFacet(dim, option)` — text search, then other dims fully, relax same-dim include,
  keep same-dim exclude.
- `countExcludeImpact(dim, option)` — text search, then other dims fully, no D_in, count
  rows where `row[dim] == option`.

## Fingerprint

The fingerprint string includes all 8 state fields:

```
team_in=...|team_out=...|status_in=...|status_out=...|region_in=...|region_out=...|query=...|sort=...
```

## Rendering additions (PROMPT_64)

### Search input (RULE 4)

Rendered at the top of `<aside id="filter-panel">` in the Zmpl template:

```html
<input type="text" name="query" value="{{query}}"
       data-role="search-input" data-search-query="{{query}}"
       hx-get="/ui/reports/results" hx-target="#report-results"
       hx-trigger="keyup changed delay:300ms" hx-include="#report-filters"
       placeholder="Search reports..." />
```

### Sort select (RULE 5)

Rendered inside `<main id="report-results-container">` above `#report-results`:

```html
<select name="sort" data-role="sort-select" data-sort-order="{{sort}}"
        hx-get="/ui/reports/results" hx-target="#report-results" hx-include="#report-filters">
  <option value="events_desc" @if (sort_events_desc_selected) { selected }>Events: high → low</option>
  <option value="events_asc"  @if (sort_events_asc_selected)  { selected }>Events: low → high</option>
  <option value="name_asc"    @if (sort_name_asc_selected)    { selected }>Name: A → Z</option>
</select>
```

Handler passes `sort_events_desc_selected`, `sort_events_asc_selected`, and
`sort_name_asc_selected` booleans so the selected option persists across HTMX swaps.

### Independent scroll layout (RULE 6)

The template's top-level element carries `data-role="reports-layout"`:

```html
<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">
  <aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4 space-y-4">
    ...
  </aside>
  <main id="report-results-container" class="flex-1 overflow-y-auto p-4">
    ...
  </main>
</div>
```

The layout wrapper is NOT a partial swap target. Only `id="report-results"` is swapped
by HTMX. Each column scrolls independently via `overflow-y-auto`.

### `#report-results` data attributes

```html
<section id="report-results"
         data-search-query="{{query}}"
         data-sort-order="{{sort}}"
         class="space-y-2 mt-3">
```

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

Sort select state: `sort_events_desc_selected`, `sort_events_asc_selected`,
`sort_name_asc_selected` (boolean). Also `query` and `sort` (strings).

Row list: `rows` (array of objects with `report_id`, `team`, `status`, `region`, `events`).

All option `<label>` elements carry `data-filter-dimension`, `data-filter-option`,
`data-filter-mode`, `data-option-count`. Quick exclude labels carry `data-role="quick-exclude"`,
`data-quick-exclude-dimension`, `data-quick-exclude-value`, `data-active`.

Search input: `data-role="search-input"`, `data-search-query`.
Sort select: `data-role="sort-select"`, `data-sort-order`.
Results section: `id="report-results"`, `data-search-query`, `data-sort-order`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/zig-zap-jetzig-faceted-filter-example.zig`
- `examples/canonical-api/zig-zap-jetzig-faceted-filter-panel-template.zmpl`
