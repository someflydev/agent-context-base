# Canonical Storage Examples

Use this category for preferred patterns around databases, caches, queues, search systems, and vector stores.

Primary files in this category:

- `duckdb-polars-example.py`
- `redis-mongo-shape-example.md`

## A Strong Canonical Storage Example Should Show

- storage client or adapter boundary
- Docker-backed dev and test isolation
- one real write path and one real read or query path
- minimal integration-test structure against isolated test infrastructure
- any seed, fixture, or reset behavior needed for repeatability

## Choosing This Example

Choose this category when the main implementation question is about wiring a storage boundary correctly.

## Drift To Avoid

- storage logic demonstrated only through mocks
- examples that share dev and test data
- one huge multi-backend example that is hard to adapt safely
