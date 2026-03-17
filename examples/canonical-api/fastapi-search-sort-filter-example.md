# FastAPI Search, Sort, and Scroll Layout Example

## Purpose

Extends the split include/exclude filter panel pattern
(`fastapi-split-filter-panel-example.py`) with three PROMPT_64 features:

- **Text search** (RULE 4): a free-text input that narrows results and counts before any
  facet logic runs.
- **Sort order** (RULE 5): a dropdown that controls result display order without affecting
  any counts.
- **Independent scroll layout** (RULE 6): CSS-only approach where the filter panel and
  results section scroll independently.

## Extended query state (two new fields)

The `QueryState` dataclass now has eight fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `team_in` | `list[str]` | `[]` | Include filter for team dimension |
| `team_out` | `list[str]` | `[]` | Exclude filter for team dimension |
| `status_in` | `list[str]` | `[]` | Include filter for status dimension |
| `status_out` | `list[str]` | `[]` | Exclude filter for status dimension |
| `region_in` | `list[str]` | `[]` | Include filter for region dimension |
| `region_out` | `list[str]` | `[]` | Exclude filter for region dimension |
| `query` | `str` | `""` | Text search term (normalized: trimmed, lowercased) |
| `sort` | `str` | `"events_desc"` | Sort order; invalid values default to `"events_desc"` |

## Text search semantics (RULE 4)

`apply_text_search(rows, query)` performs a case-insensitive substring match on
`report_id`. It returns all rows when `query` is empty.

**Application order** — `apply_text_search` is always called first:
- `filter_rows(state)` → apply Q, then apply dimension filters.
- `facet_counts(state, dimension)` → apply Q first, then compute counts with
  same-dimension include relaxation. Q is never relaxed.
- `exclude_impact_counts(state, dimension)` → apply Q first, then apply other-dimension
  filters, then count per option.

The result-count badge always reflects rows passing both Q and all active facet filters.
Facet option counts reflect the search-narrowed working set. Computing counts against the
pre-search dataset when Q is active is a correctness failure.

### Example with `query="daily"`

Dataset: 6 rows. Only `daily-signups` contains "daily" in `report_id`.

- Result count: 1
- team/growth: 1, team/platform: 0
- status/active: 1, status/paused: 0, status/archived: 0
- region/us: 1, region/eu: 0, region/apac: 0

## Sort order semantics (RULE 5)

`sort_rows(rows, sort_value)` sorts the result list only. It is never called inside
`facet_counts` or `exclude_impact_counts`.

| `sort` value | Behaviour |
|---|---|
| `events_desc` | Numeric descending by `events`; tiebreak: `report_id` ascending |
| `events_asc` | Numeric ascending by `events`; tiebreak: `report_id` ascending |
| `name_asc` | Lexicographic ascending by `report_id` |

Default order (no param or invalid value): `events_desc`.

With `sort=events_asc`, `legacy-import` (events: 4) is first.
With `sort=name_asc`, `api-latency` (alphabetically first) is first.

## Independent scroll layout (RULE 6)

The full-page response wraps the layout in:

```html
<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">
  <aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">
    <!-- filter panel: search input, quick excludes, dimension groups -->
  </aside>
  <main id="report-results-container" class="flex-1 overflow-y-auto p-4">
    <!-- result-count badge, sort select, id="report-results" -->
  </main>
</div>
```

The layout wrapper is rendered once on full page load and is **never** a partial swap
target. HTMX swaps replace only `id="report-results"` (and OOB-swap the result-count
badge). Scroll positions are preserved across filter updates.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ui/reports` | Full page with independent scroll layout |
| GET | `/ui/reports/results` | HTMX partial: OOB badge + results section |
| GET | `/ui/reports/filter-panel` | HTMX partial: filter panel (includes search input) |
| GET | `/healthz` | Health check |

All endpoints accept the same eight query parameters:
`team_in`, `team_out`, `status_in`, `status_out`, `region_in`, `region_out`,
`query` (single string), `sort` (single string).

## Data contract (additions to the existing data-* attribute set)

**Search input element:**
```
name="query"
data-role="search-input"
data-search-query="{current Q value}"
hx-trigger="keyup changed delay:300ms"
```

**Sort select element:**
```
name="sort"
data-role="sort-select"
data-sort-order="{current sort value}"
```

**Results section (`id="report-results"`) — additions:**
```
data-search-query="{current Q value}"
data-sort-order="{current sort value}"
```

**Layout wrapper:**
```
data-role="reports-layout"
id="reports-layout"
```

All existing PROMPT_50/51 data-* attributes on option elements, quick-exclude toggles,
and the results section remain unchanged.

## Related

- `context/doctrine/search-sort-scroll-layout.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/README-faceted-filter-examples.md`
- `examples/canonical-integration-tests/playwright-search-sort-example.spec.ts`
