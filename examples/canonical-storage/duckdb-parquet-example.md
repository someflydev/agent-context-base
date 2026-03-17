# DuckDB + Parquet Local Round-Trip Example

**Verification level: structure-verified**
(This example is not yet behavior-verified; a docker-compose harness under
`verification/scenarios/duckdb_parquet_min_app/` is the follow-on task.)
Harness: none yet

This example is the reference for the local Parquet write + DuckDB query round-trip.
It is structurally distinct from `duckdb-polars-example.py` (which uses in-memory DuckDB
SQL tables, not Parquet files) and from `parquet-minio-example.py` (which writes to MinIO).

See `duckdb-parquet-example.py` for the runnable implementation.

---

## When To Use This Example

Use this example when:
- The repo reads Parquet files from a local directory (not MinIO/S3).
- The query layer is DuckDB (SQL-based, with partition pruning via `hive_partitioning=true`).
- The downstream consumer expects a Polars DataFrame.
- The data is written by PyArrow with a pinned schema.

Do NOT use this example when:
- **Data lives in MinIO or S3** — use `parquet-minio-example.py` for the write path and its `read_back()` for the S3 DuckDB read path. That function configures the `httpfs` extension required for S3 access.
- **DuckDB is used for in-memory SQL tables (no Parquet files)** — use `duckdb-polars-example.py`. That example creates a DuckDB table, inserts rows, and returns a Polars DataFrame via `pl.read_database()`.
- **Trino is the query layer** — use `trino-federated-analytics-example.sql` when the query spans multiple storage systems.

---

## Write Path: PyArrow with Pinned Schema

PyArrow is the canonical write path for primary Parquet writes (not DuckDB `COPY TO`) for three reasons:

1. **The schema is explicit.** The `SCHEMA` constant is defined at module level using `pa.schema()` with explicit field types and nullability. Schema inference from the first batch is avoided — inference produces silent type coercion when empty batches or nullable columns appear in practice. See `context/stacks/parquet.md` for the full schema evolution rules.

2. **Partition directories are created explicitly by the writer.** The `write_fixtures()` function calls `path.mkdir(parents=True, exist_ok=True)` before `pq.write_table()`. PyArrow raises `FileNotFoundError` if the directory does not exist. This makes the directory layout visible and intentional rather than implicitly managed.

3. **Hive-style naming is enforced at the call site.** Directory names follow the `key=value/` convention required by DuckDB's `hive_partitioning=true`:

```
docker/volumes/dev/parquet/reports/
  tenant_id=acme/
    date=2026-03-10/
      part-0001.snappy.parquet
  tenant_id=globex/
    date=2026-03-10/
      part-0001.snappy.parquet
```

Use DuckDB `COPY TO` only for intermediate query results where schema inference from the source query is acceptable and the write is not the primary production write path.

---

## DuckDB Read Path: `hive_partitioning=true`

The `hive_partitioning=true` flag changes how DuckDB resolves the glob pattern:

**Without `hive_partitioning=true`:** DuckDB treats directory names as path components only. The `tenant_id` and `date` values in the directory names are not parsed; they are absent from the result set. A `WHERE tenant_id = 'acme'` clause has no column to filter on and raises an error.

**With `hive_partitioning=true`:** DuckDB parses `key=value` directory names and injects each key as a virtual column in the result set. The `WHERE tenant_id = 'acme'` clause is pushed down to directory selection — DuckDB identifies which directories match the predicate before opening any files, and skips non-matching directories entirely. For a dataset with 100 tenant partitions, a single-tenant query opens 1 directory, not 100.

Requirements for `hive_partitioning=true` to work correctly:
- Directory names must follow `key=value/` format exactly — case matters, underscores matter.
- Any directory that does not follow this format will have a NULL value for the partition column.
- The partition keys (`tenant_id`, `date`) are virtual columns injected by DuckDB; they do not need to appear in the Parquet file's physical schema.

---

## Polars Output: `pl.from_arrow()` vs `pl.read_database()`

The `query()` function returns a Polars DataFrame using:

```python
rel = conn.sql("SELECT ... FROM read_parquet(...)")
df = pl.from_arrow(rel.arrow())
```

**Why `pl.from_arrow(rel.arrow())` and not `pl.read_database()`:**

- `conn.sql(...)` returns a DuckDB relation object, not a result set. `pl.from_arrow(rel.arrow())` converts this relation to a Polars DataFrame via Arrow IPC — zero SQL round-trip, schema preserved exactly as DuckDB resolves it.
- `pl.read_database()` accepts a SQL string and a connection object. It is the correct interface for querying in-memory DuckDB tables (as in `duckdb-polars-example.py`), but it does not accept a DuckDB relation object as input.
- The `from_arrow` path is also more efficient: the Arrow columnar format moves from DuckDB's internal representation to Polars without any intermediate serialization to Python lists or tuples.

When you need to compose a DuckDB SQL query with downstream Polars transforms, this pattern is the canonical bridge:

```python
conn = duckdb.connect()
rel = conn.sql("SELECT ... FROM read_parquet(..., hive_partitioning=true) WHERE ...")
df = pl.from_arrow(rel.arrow())
# Apply Polars transforms to df here
```

---

## Connection Mode: In-Memory vs File-Backed

This example uses `duckdb.connect()` with no arguments — an in-memory connection. No `.duckdb` file is created on disk. The connection holds no state beyond the current session.

**Use in-memory (`duckdb.connect()`) for:**
- Read-only `read_parquet()` scans — the connection closes cleanly when the session ends; no cleanup required.
- CI and test environments — no artifact files to clean up between test runs.
- Any case where the query result is consumed immediately and not cached.

**Use file-backed (`duckdb.connect('path.duckdb')`) only when:**
- Caching the result of a slow aggregation into a persistent DuckDB table for repeated interactive queries.
- Building a local analytical warehouse where query results must survive process restarts.

Do not use a file-backed connection for `read_parquet` scanning of volatile data directories. The DuckDB catalog file accumulates metadata about the scanned paths; as Parquet files change between scans, the catalog metadata becomes stale and can cause unexpected query behavior.

---

## Relationship To Other Storage Examples

| Example | Data lives | Write path | DuckDB access | Output |
|---|---|---|---|---|
| `duckdb-polars-example.py` | In-memory DuckDB table | DuckDB SQL `INSERT` | File-backed embedded (or in-memory) | Polars DataFrame via `pl.read_database()` |
| `duckdb-parquet-example.py` | Local Parquet files | PyArrow `pq.write_table()` | In-memory `read_parquet()` with `hive_partitioning=true` | Polars DataFrame via `pl.from_arrow()` |
| `parquet-minio-example.py` | MinIO S3 bucket | PyArrow + boto3 upload | DuckDB `httpfs` extension | Row count scalar |

**Composition:** When a repo uses the local Parquet write path and also needs federated queries across MinIO, load this example for the local pipeline and `parquet-minio-example.py` for the object store write path. Do not use this example's `DATA_DIR` path for S3 reads — they are separate responsibilities.
