# Backend API Service

Use this archetype for single-service backend repos that expose HTTP APIs and may depend on storage, queues, or search.

## Common Goals

- clear transport and domain boundaries
- reliable boot path
- predictable local dev and test infrastructure
- smoke-tested main routes

## Required Context

- `context/doctrine/testing-philosophy.md`
- `context/doctrine/compose-port-and-data-isolation.md`
- the active web stack doc

## Common Workflows

- `context/workflows/add-api-endpoint.md`
- `context/workflows/add-storage-integration.md`
- `context/workflows/add-smoke-tests.md`
- `context/workflows/add-deployment-support.md`

## Likely Examples

- `examples/canonical-api/README.md`
- `examples/canonical-smoke-tests/README.md`
- `examples/canonical-storage/README.md`

## Typical Anti-Patterns

- controller or handler bloat
- no real-infra tests for storage-backed behavior
- one repo trying to be many deployable services

