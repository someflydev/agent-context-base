# Canonical Integration Test Examples

Use this category when the change crosses a real storage or service boundary and smoke tests alone would be misleading.

## When to Use This Category

Choose `canonical-integration-tests/` when:

- the test must write to and read from a real database, cache, or queue container
- the test must verify that HTMX fragment responses, filter counts, or Plotly chart payloads reflect backend query state correctly
- the test represents a critical user journey (CUJ) that spans multiple UI interactions

Use `canonical-smoke-tests/` instead when the goal is the smallest possible happy-path check against a running service — not a real-infra write/read assertion.

## Files in This Category

### Database integration test

- `fastapi-db-integration-test-example.py` — FastAPI + PostgreSQL integration test pattern. Shows `docker-compose.test.yml` boot, fixture data insertion, a real write, a real read assertion, and explicit teardown. Use this as the reference shape for any new backend service that needs real-database integration coverage.

### Single-feature Playwright tests

These tests verify one backend-driven UI behavior in isolation. Each uses a real running service and asserts that the server-side response (HTMX fragment, JSON payload, or count field) is correct.

- `playwright-backend-filtering-example.spec.ts` — verifies that activating a filter produces the correct HTMX fragment and that the result set matches the filter predicate
- `playwright-filter-counts-example.spec.ts` — verifies that per-facet counts in the filter panel are exact and update correctly when filters change
- `playwright-search-sort-example.spec.ts` — verifies the search → sort → result-display sequence: keyword search returns correct rows, sort changes reorder results deterministically
- `playwright-split-filter-panel-example.spec.ts` — verifies the split include/exclude filter panel: including a facet adds records, excluding a facet removes them, counts update correctly

### CUJ Playwright tests

CUJ (critical user journey) tests cover multi-step user flows. They are longer than single-feature tests and prove that the full interaction sequence works end-to-end.

- `playwright-cuj-filter-example.spec.ts` — 10 CUJ tests using a page object model; covers load, apply filter, clear filter, multi-select, exclude, keyword search, sort, scroll, count verification, and reset-all flows

## Strong Examples in This Category Show

- `docker-compose.test.yml` as the only target for reset and fixture flows — never the dev compose
- explicit boot and teardown of the test stack before and after the suite
- a real write and a real read or query assertion, not a mocked boundary
- small deterministic fixture data (enough to make the assertions meaningful, not a full production seed)
- Playwright assertions that prove backend-driven UI semantics when the interface depends on HTMX fragments, facet counts, or chart payloads

## Related

- `context/workflows/add-playwright-ui-verification.md`
- `context/stacks/backend-driven-ui-htmx-tailwind-plotly.md`
- `examples/canonical-smoke-tests/` for lighter happy-path checks
