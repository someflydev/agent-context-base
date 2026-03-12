# Data Pipeline

Use this archetype for repos that ingest, transform, and emit data as a primary concern.

## Common Goals

- deterministic small fixtures
- clear transform stages
- repeatable local runs
- explicit storage boundaries

## Required Context

- `context/doctrine/testing-philosophy.md`
- `context/stacks/duckdb-trino-polars.md`

## Common Workflows

- `context/workflows/add-feature.md`
- `context/workflows/add-storage-integration.md`
- `context/workflows/add-seed-data.md`

## Likely Examples

- `examples/canonical-seed-data/README.md`
- `examples/canonical-storage/README.md`

## Typical Anti-Patterns

- oversized fixtures
- hidden schema assumptions
- no real query verification for the first important boundary

