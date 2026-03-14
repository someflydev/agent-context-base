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

## Common Assistant Mistakes

- treating HTMX responses as lightweight text instead of a contract surface
- computing chart data separately from the filtered result query
- relying on frontend state to infer filters the backend never normalized
- writing Playwright specs that prove clicks but not semantics
