# Canonical Integration Test Examples

Use this category when the change crosses a real storage or service boundary and smoke tests alone would be misleading.

## Prerequisite: docker-compose.test.yml

All integration tests in this category require the test infrastructure stack to be running before
execution. The standard flow:

```bash
docker compose -f docker-compose.test.yml up -d
# wait for health checks to pass
<run integration tests>
docker compose -f docker-compose.test.yml down
```

Never run integration tests against the dev compose stack (`docker-compose.yml`). The test stack
must be isolated so that tests can safely reset and seed state without touching dev data.

The derived repo's README or a Makefile target should document this flow so any contributor can
reproduce it without reading the test code first.

## No CI Until Asked

Do not add GitHub Actions or other CI workflows for integration tests until the operator explicitly
requests it. Integration tests should reliably pass locally before they are wired into any pipeline.

## When to Use This Category

Choose `canonical-integration-tests/` when:

- the test must write to and read from a real database, cache, or queue container
- the test must verify that HTMX fragment responses, filter counts, or Plotly chart payloads reflect backend query state correctly
- the test represents a critical user journey (CUJ) that spans multiple UI interactions

Use `canonical-smoke-tests/` instead when the goal is the smallest possible happy-path check against a running service — not a real-infra write/read assertion.

## Files in This Category

### Database integration test

- `fastapi-db-integration-test-example.py` — FastAPI + PostgreSQL integration test pattern. Shows `docker-compose.test.yml` boot, fixture data insertion, a real write, a real read assertion, and explicit teardown. Use this as the reference shape for any new backend service that needs real-database integration coverage.

  Invocation:
  ```bash
  .venv_tools/bin/pytest tests/integration/ -v
  ```

### Single-feature Playwright tests (TypeScript / Bun)

These tests verify one backend-driven UI behavior in isolation. Each uses a real running service and asserts that the server-side response (HTMX fragment, JSON payload, or count field) is correct.

- `playwright-backend-filtering-example.spec.ts` — verifies that activating a filter produces the correct HTMX fragment and that the result set matches the filter predicate
- `playwright-filter-counts-example.spec.ts` — verifies that per-facet counts in the filter panel are exact and update correctly when filters change
- `playwright-search-sort-example.spec.ts` — verifies the search → sort → result-display sequence: keyword search returns correct rows, sort changes reorder results deterministically
- `playwright-split-filter-panel-example.spec.ts` — verifies the split include/exclude filter panel: including a facet adds records, excluding a facet removes them, counts update correctly

### CUJ Playwright tests (TypeScript / Bun)

CUJ (critical user journey) tests cover multi-step user flows. They are longer than single-feature tests and prove that the full interaction sequence works end-to-end.

- `playwright-cuj-filter-example.spec.ts` — 10 CUJ tests using a page object model; covers load, apply filter, clear filter, multi-select, exclude, keyword search, sort, scroll, count verification, and reset-all flows

### Playwright tests for non-TypeScript HTMX backends

Use these when the backend is Go or Python, not a Node/Bun runtime. The assertions follow the
same semantic pattern (fragment count, count label, facet update) as the TypeScript examples.

- `playwright-go-htmx-example_test.go` — playwright-go test for a Go/Echo/templ backend. Uses
  `TestMain` for browser lifecycle, individual test functions for page-scoped tests. Run with
  `go test ./tests/e2e/...`. Requires `github.com/playwright-community/playwright-go`.
- `playwright-python-htmx-example.py` — pytest-playwright test for a Python/FastAPI backend.
  Uses the `page` fixture injected by pytest-playwright. Run with
  `.venv_tools/bin/pytest tests/e2e/`. Requires `pytest-playwright` in `.venv_tools/`.

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
