# PostgreSQL

Use this pack when a repo uses PostgreSQL as its primary transactional SQL database. PostgreSQL is the default baseline for backend services that need durable, relational storage with strong consistency, schema migrations, and expressive query support. Many backend repos in this ecosystem implicitly assume PostgreSQL even when it is not stated explicitly.

This pack covers the baseline relational layer. If the repo also uses TimescaleDB, load `context/stacks/timescaledb.md` alongside this one — TimescaleDB is an extension on top of PostgreSQL, not a replacement for this pack.

## Typical Repo Surface

- `db/migrations/*.sql` or ORM migration files — ordered, numbered migration files
- `app/db/*.py` or `app/repositories/*.py` — query and transaction modules
- `app/models/*.py` — ORM model definitions or dataclass-backed query results
- `scripts/seed_data.py` or `scripts/seed_data.sql` — inserts representative rows for dev and test
- `scripts/reset_db.py` or `scripts/reset_db.sh` — drops and recreates the test database
- `docker-compose.yml` / `docker-compose.test.yml` — `postgres` service with separate named volumes and ports
- `.env` / `.env.test` — `DATABASE_URL` pointing to dev and test instances respectively

## Schema and Migration Discipline

- Number migrations sequentially and monotonically. Never modify an applied migration — always add a new one.
- Each migration should be independently reversible where practical. Document when it cannot be.
- Prefer explicit column types over generic `text` or `jsonb` when the shape is well-known and stable.
- Use `jsonb` when document shape varies meaningfully or when querying into nested fields is necessary. Do not use `jsonb` as a substitute for proper schema design — if every row has the same fields, define columns.
- Test migrations against the test database before applying to dev. A partially applied migration is not automatically rolled back.

## Indexing

- Add an index when a `WHERE`, `JOIN`, or `ORDER BY` clause on that column appears in high-frequency queries.
- Prefer partial indexes (`WHERE condition`) for sparse data — smaller, faster, and more selective than full-column indexes.
- Use `CREATE INDEX CONCURRENTLY` on live tables to avoid acquiring a table lock.
- Confirm index usage with `EXPLAIN ANALYZE` after adding an index — the planner does not always choose a new index immediately.

## Transactional Behavior

- Wrap multi-step writes in explicit transactions. Do not rely on autocommit for operations that must be atomic.
- Use `SELECT ... FOR UPDATE` or advisory locks for coordination when concurrent writers are expected on the same rows.
- Be explicit about isolation level when read committed (the default) is insufficient for the workload.

## Connection Setup

- Use a connection pool (`asyncpg`, `psycopg3`, `pgx`, `SQLx`, or ORM-managed pool) rather than raw driver connections in any production-facing code path.
- Set pool size appropriate to expected concurrency — do not leave library defaults unchecked.
- In test environments, use a separate database or dedicated schema to isolate test state. Do not share a database between dev and test instances.

## Reporting Queries

- Use CTEs (`WITH`) to break up complex multi-step analytical queries into readable stages.
- Use `MATERIALIZED VIEW` for expensive aggregations computed on a schedule and read frequently. Use `REFRESH MATERIALIZED VIEW CONCURRENTLY` when query freshness matters.
- Avoid large ad hoc scans on OLTP tables — move them to a read replica or a materialized summary if they affect operational latency.

## Testing Expectations

- Run all integration tests against a real isolated PostgreSQL instance (Docker-backed, separate test port)
- Prove one migration applies cleanly against the test database
- Prove one representative write plus one read that exercises the indexed query path
- For transactional logic, prove both the commit path and the rollback path
- For migration-heavy changes, prove that applying the migration to a clean schema succeeds
- Do not mock the database driver — mock boundaries hide SQL errors, type mismatches, and constraint violations

## Relationship to TimescaleDB

`postgresql.md` covers the foundational relational layer. When the repo adds time-series features via TimescaleDB:

- Load `context/stacks/timescaledb.md` alongside this pack
- TimescaleDB assumes all PostgreSQL fundamentals are already addressed
- Hypertables, retention policies, and continuous aggregates are TimescaleDB concerns; schema design, indexing, connection setup, and migration discipline belong here

## Common Assistant Mistakes

- Using `jsonb` everywhere to avoid defining a schema — if the data is relational, model it relationally
- Not writing a migration file and instead altering the schema manually or in application startup code
- Sharing the dev database with integration tests — always use separate instances or at minimum separate databases
- Forgetting to run `EXPLAIN ANALYZE` after adding an index to confirm it is being used by the planner
- Using `SELECT *` in application query modules — project explicitly to avoid shape surprises when columns are added or reordered
- Missing explicit transaction boundaries on multi-step writes that must be atomic
