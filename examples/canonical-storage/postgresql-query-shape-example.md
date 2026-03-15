# PostgreSQL Query Shape Example

This example demonstrates representative PostgreSQL patterns for transactional storage and reporting
queries.

## When PostgreSQL Is the Right Tool

Use PostgreSQL for:

- OLTP workloads: inserts, updates, deletes, transactional reads
- analytical queries on local data where the result set fits in memory
- schema-enforced data where migrations manage evolution
- bounded jsonb metadata where the field set is known and queryable

Do not use PostgreSQL for:

- cross-database joins that span separate storage systems (use Trino for that)
- large-scale horizontal scans over billions of rows (consider DuckDB or Trino)
- document-model workloads with deeply variable schema (consider MongoDB)

## SQL File

The companion SQL file is `postgresql-query-shape-example.sql`.

## Schema Design Notes

### Status as a checked text column

Using a `CHECK` constraint on a `TEXT` column rather than a custom `ENUM` type avoids the pain of
`ALTER TYPE ADD VALUE` not being transactional in PostgreSQL. If the status set is small and stable,
an enum is fine; if it grows across migrations, a check constraint is easier.

### Partial indexes

```sql
CREATE INDEX idx_report_runs_tenant_report
    ON report_runs (tenant_id, report_id, requested_at DESC)
    WHERE status = 'ready';
```

This index only covers rows where `status = 'ready'`, which is the hottest filter path in reporting
queries. Rows in `queued`, `running`, or `failed` states are excluded. Partial indexes are appropriate
when a large fraction of rows will never match the common query predicate, and using `WHERE` keeps the
index small and fast to update.

Always include `IF NOT EXISTS` in migration files to make them safe to replay.

### Bounded jsonb

```sql
metadata JSONB
```

Use `jsonb` for genuinely variable secondary attributes. Keep the field set bounded: if every row will
always have a field, make it a proper column. Index a specific path when queries filter on it:

```sql
CREATE INDEX idx_report_runs_metadata_source
    ON report_runs ((metadata->>'source'))
    WHERE metadata ? 'source';
```

Do not store large arrays or unbounded nested documents in a `jsonb` column. Those shapes belong in a
document store.

## Reporting Query Notes

The weekly reporting query uses a CTE (`WITH` clause) to keep aggregation logic readable and to allow
`ROW_NUMBER()` to operate on the aggregated result rather than the raw table.

```sql
PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_ms)
    FILTER (WHERE status = 'ready')
```

`PERCENTILE_CONT` is an ordered-set aggregate. The `FILTER` clause narrows it to successful rows only.
This is standard PostgreSQL; it does not require an extension.

## Materialized View Pattern

When a reporting query runs frequently against a large table, a materialized view with
`REFRESH MATERIALIZED VIEW CONCURRENTLY` is the right pattern:

- the view pre-aggregates the expensive scan
- `CONCURRENTLY` allows reads during the refresh, which requires a `UNIQUE INDEX` on the view
- refresh is triggered by a scheduled job or a post-write hook, not on every request

This is preferable to an application-side cache for reporting aggregates because the database owns the
correctness guarantee.

## Migration Discipline

- Always create indexes `CONCURRENTLY` in production to avoid table locks
- Use `IF NOT EXISTS` on all DDL in migration files to make them replayable
- Keep migrations append-only and numbered; never edit an applied migration

## Trino vs. PostgreSQL

See `trino-federated-analytics-example.md` for when to route analytics to Trino instead of running
the query locally in PostgreSQL.

## Verification Level

Structure-verified (file existence and SQL marker checks only). No live PostgreSQL instance is wired
in the default verification tier.
