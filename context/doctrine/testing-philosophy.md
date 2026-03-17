# Testing Philosophy

Testing should match the real risk surface.

## Default Test Layers

Most repos derived from this base should have:

- focused unit tests for local logic
- smoke tests for key happy paths
- minimal real-infra integration tests for meaningful boundaries

Not every change needs every layer, but significant behavior should not rely on smoke tests alone.

## Unit Tests: When and What

Unit tests are the right layer for pure logic that does not require real infrastructure:

- input validation functions and business rule checks
- data transforms, filter query builders, aggregation helpers
- request/response model serialization and coercion
- parameterized edge cases where fast coverage of many inputs matters

**Correct:** test a filter-query builder function with 10 parameterized input/output cases.

**Wrong:** test a route handler as a "unit test" when it requires a real database connection to
mean anything. That is an integration test wearing a unit test costume, and it will either silently
skip the boundary (producing false confidence) or fail in an opaque way.

Unit tests may use mocks and stubs for isolated logic. That is their appropriate scope.

## Integration Tests: When and What

Integration tests are the right layer for any change that crosses a real storage, queue, search,
or service boundary. An integration test must include at least one real write and one real read or
query assertion against the actual service.

Integration tests are required when a change touches:

- database writes or query behavior
- cache coherence
- message publication or consumption
- search indexing or retrieval
- vector indexing or retrieval
- service-to-service contracts

The docker-compose.test.yml stack must be up before integration tests run. Integration tests must
never substitute a mock, in-memory store, or stub for the real service. See "The Mock Anti-Pattern"
below.

## The Mock Anti-Pattern

Mocking the storage layer in an integration test produces a test that cannot catch the class of
failures it exists to prevent:

- schema drift between application code and the actual database schema
- migration errors that only surface against a real query planner
- constraint violations that a mock simply ignores
- query plan differences between SQLite and Postgres

**Unit tests may use mocks and stubs.** That is appropriate.

**Integration tests must not.** Specific anti-patterns to avoid:

- using SQLite in-memory as a stand-in for a Postgres integration test
- patching the storage adapter with `unittest.mock` inside an integration test suite
- replacing a real message broker with an in-memory fake that does not exercise pub/sub semantics
- using an in-memory vector index when the boundary under test is a real vector store

If a test uses a real HTTP client but a mocked database, it is not an integration test — it is a
unit test with extra routing. Call it what it is, or make it real.

## Test File Layout

The canonical layout for derived repos:

```
tests/
  unit/             # pure logic: validators, transforms, data models, algorithms
  integration/      # storage and service boundaries — requires docker-compose.test.yml
  e2e/              # Playwright — requires the running app + docker-compose.test.yml
```

Each directory should have its own README if the suite is non-trivial. The README in
`tests/integration/` should document the docker-compose.test.yml prerequisite explicitly.

## Running Integration Tests

The docker-compose.test.yml stack must be up before integration tests run. The standard flow:

```bash
docker compose -f docker-compose.test.yml up -d
# wait for health checks to pass
<run integration tests>
docker compose -f docker-compose.test.yml down
```

The derived repo's README or a Makefile target should document this flow. Never run integration
tests against the dev compose stack (`docker-compose.yml`). The test stack must be isolated.

## CI: Do Not Add Until Asked

GitHub Actions (or any other CI platform) must not be added to a derived repo until the operator
explicitly requests it.

Reasons:
- CI adds maintenance surface before the test suite is stable
- Broken CI on every push discourages good test hygiene during early development
- The right moment for CI is when the integration tests reliably pass locally

This rule applies to: `.github/workflows/`, Makefile CI targets, any automation that runs on push
or merge. Local Makefile helpers for running tests are fine — those are for the developer, not
the pipeline.

## Smoke Tests vs Integration Tests

These are different tools with different prerequisites:

**Smoke tests** confirm the app boots and the happy path responds. They do not require real
infrastructure if the app can start without it (use test environment variables to skip infra
checks on boot). A smoke test should be runnable in seconds against a local process.

**Integration tests** prove a real boundary works. They always require docker-compose.test.yml
to be up. They are slower and more deliberate.

Never conflate the two. A smoke test that requires full infrastructure to be up is not a smoke
test — it is an integration test with fewer assertions.

## When Integration Tests Become Required

Add minimal real-infra integration tests when a change touches:

- database writes or query behavior
- cache coherence
- message publication or consumption
- search indexing or retrieval
- vector indexing or retrieval
- service-to-service contracts

The goal is not exhaustive coverage. The goal is to prove the boundary works against real
dependencies in an isolated test stack.

## Happy Path First, Then A Few Edges

For significant features, test:

1. the mostly happy path
2. one or two meaningful edge cases
3. obvious failure handling if it is part of the feature contract

## Keep Test Stacks Real But Small

Use Docker-backed test infrastructure where it matters. Keep it isolated, reproducible, and boring.

## Anti-Patterns

- replacing all integration testing with mocks
- writing broad flaky end-to-end suites when a focused integration test would do
- coupling tests to dev data
- treating smoke tests as the only production-safety signal
- adding CI workflows before integration tests pass reliably locally
