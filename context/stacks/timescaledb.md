# TimescaleDB

Use this pack when the repo stores time-series analytics in PostgreSQL with TimescaleDB features. TimescaleDB is an extension on top of PostgreSQL — it is not a standalone database. When loading this pack, also load `context/stacks/postgresql.md` for baseline connection, migration, indexing, and testing conventions.

`postgresql.md` covers the foundations. This pack covers only the TimescaleDB-specific concerns layered on top of those foundations.

## Typical Repo Surface

- `db/migrations/*.sql` — includes hypertable creation, compression settings, and retention policy setup
- `app/queries/*.py` or `app/queries/*.sql` — time-window queries, rollup queries, continuous aggregate queries
- `app/jobs/*.py` or scheduler config — ingestion jobs that write to hypertables
- `docker-compose.yml` / `docker-compose.test.yml` — `timescaledb/timescaledb:latest-pg16` (or equivalent version-pinned image), not plain `postgres`

## Change Surfaces To Watch

- **Hypertable creation**: `SELECT create_hypertable(...)` must appear in a migration file, not in application startup code. The chunk interval should match the expected query pattern (hourly, daily, weekly).
- **Retention policies**: set via `add_retention_policy`. Know which chunk interval aligns with the intended retention window.
- **Continuous aggregates**: `CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous)` — refresh policies matter. Stale aggregates cause silent result drift.
- **Compression**: `add_compression_policy` — verify that compressed chunks are excluded from or handled correctly in any write paths that touch historical data.
- **Write path shape**: TimescaleDB performs best with time-ordered inserts into hypertables. Backfill patterns may require explicit chunk management.

## Testing Expectations

- Run integration tests against a real TimescaleDB-enabled instance (the `timescaledb/timescaledb` Docker image, not plain `postgres` — TimescaleDB features are unavailable on plain postgres)
- Prove one write path into a hypertable and one representative aggregate query against fixture data
- For continuous aggregates, prove that a refresh produces the expected output
- For retention policies, prove that the policy configuration is accepted without error
- Add an edge case around time windows or empty-series behavior when the query logic depends on it

## Relationship to postgresql.md

TimescaleDB inherits everything from PostgreSQL. Before implementing TimescaleDB-specific features:

- Connection setup, migration tooling, and query module conventions → `context/stacks/postgresql.md`
- Integration test isolation (separate test database, real Docker instance) → `context/stacks/postgresql.md`
- Index discipline, transaction boundaries, and connection pooling → `context/stacks/postgresql.md`

Load `postgresql.md` first, then layer TimescaleDB-specific concerns from this pack.

## Common Assistant Mistakes

- Using the plain `postgres` Docker image in Compose files — TimescaleDB extension will not be available
- Skipping migration verification for hypertable and retention policy changes
- Testing only query builders and not actual SQL behavior against a real TimescaleDB instance
- Treating TimescaleDB like plain PostgreSQL everywhere — hypertable chunk boundaries affect query planning, and some operations are not supported on compressed chunks
- Not setting a refresh policy on continuous aggregates and then depending on them for fresh query results
