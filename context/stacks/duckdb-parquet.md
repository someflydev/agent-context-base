# DuckDB + Parquet (Local File)

Use this pack when DuckDB is the query engine over Parquet files on local disk. This is the canonical pattern for local analytical pipelines and lightweight data lake prototyping that do not require object storage.

**Adjacent docs and when to use them instead:**
- Files live in MinIO or S3 → load `context/stacks/parquet-minio.md` (write path) and `context/stacks/duckdb-trino-polars.md` (read path with httpfs).
- Trino federation is required → load `context/stacks/duckdb-trino-polars.md`.
- DuckDB is used only for in-memory SQL tables with no Parquet files → `duckdb-polars-example.py` already covers that; no additional stack doc needed.

## When To Load This Pack

Load this pack when:
- The repo stores Parquet files on local disk (under `data/`, `docker/volumes/`, or a mounted path) and DuckDB is the query layer.
- The task involves writing Parquet from Python (PyArrow or DuckDB COPY TO) and reading it back with DuckDB's `read_parquet()` function.
- The pipeline is local-dev or CI-only; no object store is involved in the read path.
- The user asks about "query parquet with duckdb", "read local parquet", "duckdb scan", "partition parquet on disk", or similar.

Do NOT load this pack when:
- Files live in MinIO or S3 — load `parquet-minio.md` and `duckdb-trino-polars.md`.
- Trino federation is required — load `duckdb-trino-polars.md`.
- DuckDB is used only for in-memory SQL tables (no Parquet files) — the existing `duckdb-polars-example.py` already covers that.

## When To Use DuckDB vs Polars for Parquet Scanning

Use **DuckDB (`read_parquet`)** when:
- The query involves JOINs across multiple Parquet datasets.
- The query is an aggregation (GROUP BY, window functions, SUM/COUNT over millions of rows).
- The user already knows SQL and wants a familiar query interface.
- Hive-style partition pruning is needed: DuckDB's `hive_partitioning=true` pushes predicates into partition directory selection, skipping unneeded directories entirely.
- The result of the query needs further SQL computation before becoming a DataFrame.

Use **Polars (`scan_parquet`)** when:
- The operation is a column projection + filter with no join or aggregation.
- The transform is best expressed as a lazy Polars expression graph (`map_elements`, rolling windows, complex column operations).
- The downstream consumer expects a Polars LazyFrame for further chaining.
- The pipeline is streaming (scan in chunks without loading all rows into memory).

**Composition pattern** — both paths compose cleanly. Use DuckDB for the SQL query, then convert the result to a Polars DataFrame for downstream transforms:

```python
import duckdb
import polars as pl

conn = duckdb.connect()
rel = conn.sql("""
    SELECT tenant_id, SUM(event_count) AS total
    FROM read_parquet('data/reports/**/*.parquet', hive_partitioning=true)
    WHERE tenant_id = 'acme'
    GROUP BY tenant_id
""")
df = pl.from_arrow(rel.arrow())
# df is now a Polars DataFrame; apply further Polars transforms here
```

This composition is the canonical pattern when both a complex SQL query and a downstream Polars transform are needed.

## DuckDB Parquet Read API

### 1. Basic read with glob pattern

```python
import duckdb

conn = duckdb.connect()
rel = conn.sql("SELECT * FROM read_parquet('data/**/*.parquet')")
```

### 2. Hive-style partition pruning

```python
conn = duckdb.connect()
rel = conn.sql("""
    SELECT tenant_id, COUNT(*) AS row_count
    FROM read_parquet('data/reports/**/*.parquet', hive_partitioning=true)
    WHERE tenant_id = 'acme'
    GROUP BY tenant_id
""")
```

When `hive_partitioning=true`, DuckDB reads partition key=value pairs from directory names (e.g., `tenant_id=acme/`) and injects them as virtual columns. Predicates on those virtual columns prune directories entirely before DuckDB opens any files. A `WHERE tenant_id = 'acme'` clause means DuckDB never opens the `tenant_id=globex/` directory at all.

### 3. Union multiple directories

```python
rel = conn.sql("""
    SELECT * FROM read_parquet(['data/2026-03-10/**/*.parquet',
                                'data/2026-03-11/**/*.parquet'])
""")
```

### 4. Converting a DuckDB result to a Polars DataFrame

```python
import polars as pl

rel = conn.sql("SELECT ... FROM read_parquet(...)")
df = pl.from_arrow(rel.arrow())
```

Use `pl.from_arrow(rel.arrow())` rather than `pl.read_database()`. `from_arrow` converts a DuckDB relation object directly to a Polars DataFrame via the Arrow IPC format — no second SQL string round-trip, and the Arrow schema is preserved exactly. `pl.read_database()` accepts a SQL string and a connection object and is appropriate for in-memory DuckDB tables, not for DuckDB relation objects.

### 5. DuckDB connection mode for Parquet scanning

Use `duckdb.connect()` (in-memory, no file on disk) for read-only Parquet scans. Only use a file-backed connection (`duckdb.connect('path/to/db')`) when caching query results into persistent DuckDB tables for repeated queries. Do not mix file-backed connections with `read_parquet` scanning of volatile data directories — the DuckDB catalog file accumulates metadata that becomes stale as Parquet files change.

## DuckDB Parquet Write Path (COPY TO)

DuckDB can write Parquet directly, which is useful for intermediate query results:

```python
conn.execute("""
    COPY (SELECT tenant_id, report_id, total_events FROM staging_table)
    TO 'data/reports/tenant_id=acme/date=2026-03-10/part-0001.parquet'
    (FORMAT PARQUET, COMPRESSION 'snappy', ROW_GROUP_SIZE 131072)
""")
```

Rules:
- Always specify `COMPRESSION` explicitly — defaults vary across DuckDB versions.
- Use `snappy` for actively queried data (fast decode), `zstd` for archival (better ratio).
- `ROW_GROUP_SIZE` is in rows, not bytes. For 128 MB row groups at ~50 bytes/row, target ~2.5M rows per group. For development fixtures, 128k rows is fine.
- Create the target directory before calling `COPY TO` — DuckDB will not create it and raises a `CatalogException` if the directory is absent.
- When writing partitioned data from DuckDB, prefer writing each partition separately (once per tenant, once per date) rather than relying on a single `COPY` with a `PARTITION BY` clause — DuckDB's `PARTITION BY` in `COPY` is available but less predictable for Hive layout.

## PyArrow Write Path (Canonical)

The authoritative write path for Parquet is PyArrow, not DuckDB `COPY TO`. Use PyArrow when:
- The Arrow schema must be pinned explicitly (never inferred from data).
- The write is the primary production write path, not a DuckDB intermediate.
- Schema version tracking is required.

Reference `context/stacks/parquet.md` for the full PyArrow schema definition and evolution rules. The canonical write shape:

```python
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

SCHEMA = pa.schema([
    pa.field("tenant_id", pa.string(), nullable=False),
    pa.field("report_id", pa.string(), nullable=False),
    pa.field("event_count", pa.int32(), nullable=False),
    pa.field("schema_version", pa.int8(), nullable=False),
])

table = pa.table({
    "tenant_id": ["acme", "globex"],
    "report_id": ["r-001", "r-002"],
    "event_count": [42, 11],
    "schema_version": [1, 1],
}, schema=SCHEMA)

out_dir = Path("data/reports/tenant_id=acme/date=2026-03-10")
out_dir.mkdir(parents=True, exist_ok=True)

pq.write_table(
    table,
    out_dir / "part-0001.snappy.parquet",
    compression="snappy",
    row_group_size=131072,
)
```

Always call `path.mkdir(parents=True, exist_ok=True)` before `pq.write_table()` — PyArrow raises `FileNotFoundError` if the directory does not exist.

## Typical Repo Surface

```
data/                          — Parquet files; partitioned by Hive convention
app/parquet/writer.py          — PyArrow schema + write logic
app/parquet/reader.py          — DuckDB read_parquet() + Polars conversion
app/pipeline.py                — orchestrates write then query
scripts/write_fixtures.py      — deterministic fixture write for local dev and CI
tests/integration/test_parquet_roundtrip.py  — write, read back, assert
```

## Testing Expectations

- Write a small deterministic dataset (at least two partition keys, at least ten rows).
- Read it back with DuckDB `read_parquet()` and assert: row count, column types, and at least one partition key value.
- Assert `hive_partitioning=true` correctly filters: query for `tenant_id='acme'` and verify only acme rows are returned.
- Do not mock file I/O — write real Parquet files to a temp directory (use `tempfile.mkdtemp` in the test; clean up in `tearDown`).
- If the pipeline also returns a Polars DataFrame, assert the DataFrame schema and at least one row value.

## Change Surfaces To Watch

- **DuckDB version upgrades** can change `COPY TO` default compression and row group behavior; pin the DuckDB version in `pyproject.toml` and test after upgrades.
- **Glob pattern changes**: adding a new partition level (e.g., adding `hour=` under `date=`) breaks existing glob patterns like `'data/**/*.parquet'` if the new level changes directory depth unexpectedly. Use `**` (recursive) globs to be safe.
- **Schema drift** between the PyArrow writer `SCHEMA` constant and the DuckDB query's column expectations — treat the `SCHEMA` constant as the single source of truth.
- **`hive_partitioning=true` requires** that partition directories follow the `key=value/` format exactly — case matters, underscores matter. Any deviation causes the partition column to be NULL for that directory.

## Common Assistant Mistakes

- Using DuckDB's file-backed connection (`duckdb.connect('analytics.duckdb')`) when only `read_parquet` scanning is needed — wastes disk space and creates an unneeded file.
- Forgetting to create the partition directory before calling `COPY TO` — DuckDB raises a `FileNotFoundError` silently wrapped in a `CatalogException`.
- Mixing `hive_partitioning=true` with non-Hive directory names (e.g., a directory named `"2026-03-10"` instead of `"date=2026-03-10"`) — the partition column is silently NULL.
- Reading from MinIO or S3 with this pattern without configuring the `httpfs` extension; `read_parquet('s3://...')` silently fails without `httpfs` loaded.
- Using `pl.read_database()` instead of `pl.from_arrow(rel.arrow())` when converting a DuckDB relation to Polars — `read_database` accepts SQL strings and a connection object, not DuckDB relation objects.
