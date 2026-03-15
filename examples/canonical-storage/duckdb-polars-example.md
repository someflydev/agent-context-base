# DuckDB + Polars Example

**Verification level: behavior-verified**
Harness: `verification/scenarios/polars_data_pipeline/`
Last verified by: `verification/examples/python/test_polars_examples.py`

This example is the reference for local, embedded DuckDB used as a query engine with Polars as the output layer. It covers creating a table in a local DuckDB file, inserting rows, and returning a typed Polars DataFrame from a SQL query.

See `duckdb-polars-example.py` for the runnable implementation.

---

## When to Use This Example

Use this example when:

- The analytical data lives in a local DuckDB file under `docker/volumes/dev/`
- The query result needs to be a Polars DataFrame for downstream transformation
- The workload is development, testing, or a local analytical pipeline — not a deployed service reading from object storage
- There is no MinIO or S3 bucket involved in the read path

---

## When NOT to Use This Example

- **Data lives in MinIO or S3** — use `parquet-minio-example.py read_back()` instead. That function configures DuckDB's `httpfs` extension and reads from `s3://bucket/reports/**/*.parquet`.
- **Production ETL reading from object storage** — the local file path is not appropriate for that workload.
- **Federated cross-catalog queries** — use `trino-federated-analytics-example.sql` when the query spans multiple storage systems.

---

## Database Path Convention

The `DATABASE_PATH` constant follows the repository's volume layout:

```
docker/volumes/dev/warehouse/analytics.duckdb
```

Test workloads must use a separate path under `docker/volumes/test/` and must never share the dev DuckDB file. In repos where the distinction matters, resolve the path from an environment variable rather than hardcoding it.

---

## Polars Output Shape

`pl.read_database()` converts the DuckDB result directly to a Polars DataFrame:

```python
return pl.read_database(
    "SELECT tenant_id, report_id, total_events FROM report_runs ORDER BY total_events DESC",
    connection=connection,
)
```

This preserves the column schema and makes the result composable with the Polars transformation layer that typically follows. Contrast this with `conn.execute().fetchall()`, which returns raw Python tuples and loses all schema information — column names, nullability, and dtypes must be reconstructed manually.

---

## Relationship to `parquet-minio-example.py`

These two examples cover the two canonical DuckDB read paths in this repository:

| Example | Data lives | DuckDB access mode | Output |
|---|---|---|---|
| `duckdb-polars-example.py` | Local file (`docker/volumes/dev/`) | Embedded, file path | Polars DataFrame |
| `parquet-minio-example.py read_back()` | MinIO/S3 bucket | S3 extension via `httpfs` | Row count scalar |

Do not use `duckdb-polars-example.py` as the S3 read path. The two examples are complements, not alternatives.

---

## Composition Pattern

When a repo uses the parquet-minio write path and also needs to transform query results into a Polars DataFrame, compose both:

1. Load `parquet-minio-example.py` for the write path and the S3 read-back assertion.
2. Load `duckdb-polars-example.py` for the local analytical query layer that produces a Polars DataFrame.

Run `read_back()` from the parquet-minio example to verify the S3 write succeeded, then open the local DuckDB file and use `pl.read_database()` for any downstream Polars transformation. Do not attempt to replace the S3 read path with the local file path — they are separate responsibilities.
