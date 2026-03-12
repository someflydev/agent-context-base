# Testing Philosophy

Testing should match the real risk surface.

## Default Test Layers

Most repos derived from this base should have:

- focused unit tests for local logic
- smoke tests for key happy paths
- minimal real-infra integration tests for meaningful boundaries

Not every change needs every layer, but significant behavior should not rely on smoke tests alone.

## When Integration Tests Become Required

Add minimal real-infra integration tests when a change touches:

- database writes or query behavior
- cache coherence
- message publication or consumption
- search indexing or retrieval
- vector indexing or retrieval
- service-to-service contracts

The goal is not exhaustive coverage. The goal is to prove the boundary works against real dependencies in an isolated test stack.

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

