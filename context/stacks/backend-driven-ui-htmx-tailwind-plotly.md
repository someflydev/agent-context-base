# Backend-Driven UI: HTMX + Tailwind + Plotly

Use this pack when a backend service renders interactive HTML fragments, count surfaces, and chart payloads without introducing a frontend application framework.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- route or controller modules for pages, fragments, and chart data
- template or HTML-render helper files
- query services that own filter parsing and count semantics
- Playwright specs for backend-driven UI behavior
- focused backend tests for count and aggregation correctness

## Common Change Surfaces

- normalized query-state parsing
- HTMX fragment endpoints and out-of-band swaps
- Tailwind-backed filter and result markup with stable selectors
- Plotly data endpoints derived from live query results
- Playwright flows that verify rows, counts, and chart alignment

## Testing Expectations

- verify result rows and result count from the same query state
- verify representative facet counts under include and exclude filters
- verify chart payload alignment with the visible result state
- verify one or two backend-driven user flows with Playwright

## Split Include/Exclude Filter Panel

Backend-driven filter panels must split include and exclude options into distinct
sub-sections per dimension group. A single merged list cannot express both modes
without ambiguity.

**Structure per dimension group:**
1. Include sub-section — one labeled checkbox per option, with include/facet count.
2. Exclude sub-section — one labeled checkbox per option, with exclude impact count.

**Key rules:**
- When a value is in D_out (excluded), its include option must show count 0, carry
  `data-excluded="true"`, and render as greyed/disabled (`opacity-50 cursor-not-allowed`,
  `disabled` on the checkbox). Its exclude option must remain visually normal.
- The exclude impact count (`exclude_impact_counts(state, dimension)`) is distinct from
  `facet_counts`. It answers "how many rows does this exclusion currently remove?"
- A quick-excludes strip may appear above the dimension groups. It is declared via a
  `QUICK_EXCLUDES` backend constant and mirrors the state of the corresponding exclude
  options in the main section. Both share the same `name`/`value` form inputs.

**Data-* attribute contract (all option elements must carry these):**
```
Include option: data-filter-dimension, data-filter-option, data-filter-mode="include",
                data-option-count (0 when excluded), data-excluded="true" (when in D_out)
Exclude option: data-filter-dimension, data-filter-option, data-filter-mode="exclude",
                data-option-count (impact count), data-active="true" (when in D_out)
Quick exclude:  data-role="quick-exclude", data-quick-exclude-dimension,
                data-quick-exclude-value, data-active="true"/"false"
```

These attributes are the verification contract for Playwright tests and backend unit tests.

See `context/doctrine/filter-panel-rendering-rules.md` for the full specification and
failure mode table. See `examples/canonical-api/fastapi-split-filter-panel-example.py`
for a complete working implementation.

## Common Assistant Mistakes

- treating HTMX responses as lightweight text instead of a contract surface
- computing chart data separately from the filtered result query
- relying on frontend state to infer filters the backend never normalized
- writing Playwright specs that prove clicks but not semantics
- showing non-zero include counts for excluded values (trust failure, not cosmetic)
- deriving the exclude impact count from the facet_counts path (returns wrong values)
- greying the exclude option instead of (or in addition to) the include option
