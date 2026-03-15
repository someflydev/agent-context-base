# DuckDB + Trino + Polars — Analytical Combo

Use this pack when a repo uses DuckDB and Polars for local analytical work combined with Trino as a federated query layer over multiple sources. This pack is for repos that genuinely use these tools together — local transforms plus cross-source federation in one workflow.

If you only need Trino, load the solo pack instead:

- Trino only → `context/stacks/trino.md`

DuckDB and Polars without Trino are typically handled by the primary application stack pack.

## When To Use This Pack Over The Solo Trino Pack

- The repo has a local analytical pipeline (DuckDB or Polars transforms) and Trino as a federated query overlay
- The task involves routing data between local DuckDB files, Polars transforms, and a Trino-accessible source catalog
- The repo's pipeline tests include both local transform verification and cross-source Trino query verification

## Typical Repo Surface

- `app/pipeline.py` — transform modules using DuckDB or Polars
- `app/queries/*.sql` — Trino query modules for cross-source reads
- `etc/catalog/*.properties` — Trino catalog configuration
- `tests/smoke/test_pipeline_smoke.py` — small end-to-end local transform check
- `tests/integration/test_pipeline_round_trip.py` — round-trip test with real DuckDB files or a real Trino target
- `data/` — local data directories for DuckDB files and fixture datasets

## Change Surfaces To Watch

- Schema assumptions shared between DuckDB, Polars, and Trino — type differences across these layers cause silent failures
- Query compatibility between DuckDB SQL and Trino SQL — they are similar but not identical; test both
- Polars transform correctness — lazy versus eager evaluation behavior differs and affects output ordering
- Output file layout and naming for DuckDB intermediate files
- Trino catalog config and connector pushdown behavior — see `context/stacks/trino.md` for details

## Testing Expectations

- Smoke test one tiny end-to-end local transform with DuckDB or Polars
- Integration test cross-source Trino queries against a real Trino instance when connection or query semantics matter
- Keep fixture datasets tiny and explicit — Trino tests fail loudly on connectivity and type issues, not dataset size
- Do not conflate local transform tests with cross-source query-integration tests

## Common Assistant Mistakes

- Writing examples against unrealistic large datasets
- Ignoring type differences between DuckDB, Polars, and Trino
- Using this pack when the repo only uses one or two of these tools rather than all three together
- Conflating DuckDB transform logic tests with Trino cross-source query-integration tests
- Treating Trino as capable of writes — it is read-only; any write path must target the backing source directly
