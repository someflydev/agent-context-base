# DuckDB + Trino + Polars

Use this pack for analytic or pipeline-heavy repos that move data between local analytical workflows and federated query layers.

## Typical Repo Surface

- transform modules
- query modules
- local data directories
- ingestion jobs
- tests with tiny fixture datasets

## Change Surfaces To Watch

- schema assumptions
- query compatibility between DuckDB and Trino
- Polars transform correctness
- output file layout and naming

## Testing Expectations

- smoke test one tiny end-to-end transform
- integration tests against real DuckDB files or a real Trino target when connection or query semantics matter
- keep fixture datasets tiny and explicit

## Common Assistant Mistakes

- writing examples against unrealistic large datasets
- ignoring type differences between query engines
- conflating transform logic tests with query-integration tests

