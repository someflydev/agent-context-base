# Parquet + MinIO

Use this pack when a repo writes Parquet files to an S3-compatible bucket (MinIO or AWS S3) and the read layer is DuckDB, Polars, or Trino. This is the canonical data-lake write path for repos that use `duckdb-trino-polars` as the analytical query layer.

Load this pack alongside `context/stacks/parquet.md` (file-format discipline) and `context/stacks/minio.md` (object store setup). Load `context/stacks/duckdb-trino-polars.md` for the read-path detail.

## When To Load This Pack

- The repo writes Parquet files and stores them in an S3-compatible bucket.
- The design question is how to partition, compress, and name files so the read layer performs well.
- The read layer is DuckDB, Polars, or Trino (load the relevant read-layer pack alongside this one).

Do not load this pack if the repo reads Parquet but does not write it — in that case, load the read-layer pack only.

## Typical Repo Surface

- `app/parquet/writer.py` — Arrow schema definition, row group flush, staging-to-final rename
- `app/storage/minio.py` — MinIO client setup with env-var credentials
- `app/pipeline.py` or equivalent — orchestrates buffer, flush, and commit steps
- `tests/integration/test_parquet_minio_roundtrip.py` — write to test bucket, read back with DuckDB, assert row count
- `docker-compose.test.yml` — MinIO service for integration tests

## Write Path Discipline

### Buffer Before Flushing

Accumulate rows into an in-memory Arrow RecordBatch before writing. Flushing one row at a time produces a small-files problem that degrades both object store performance and read-layer scan speed.

Target row group size: 128 MB to 512 MB per file for large analytical workloads. For streaming writes, flush on a time or record-count threshold, not per-event.

### Staging Prefix Pattern

Write to a `_staging/` prefix during multi-part or multi-file writes. Rename (copy + delete) to the final path after all parts complete successfully.

```
# Writing:
s3://dev-report-data/_staging/tenant_id=acme/date=2026-03-10/part-0001.snappy.parquet

# After successful flush, move to final path:
s3://dev-report-data/reports/tenant_id=acme/date=2026-03-10/part-0001.snappy.parquet
```

This prevents downstream readers from discovering partial writes. Object stores have no atomic multi-file rename; the staging prefix is the practical substitute.

### Completeness Markers

If downstream consumers poll for partition completeness, write a `_SUCCESS` marker object after completing a partition write:

```
s3://dev-report-data/reports/tenant_id=acme/date=2026-03-10/_SUCCESS
```

Consumers check for the marker before listing data files. Do not rely on file listing order — object stores do not guarantee it.

### Partition Layout

Use Hive-style partition directories. The read layer (DuckDB, Polars, Trino) discovers partitions by parsing directory names.

```
reports/
  tenant_id=acme/
    date=2026-03-10/
      part-0001.snappy.parquet
      _SUCCESS
  tenant_id=globex/
    date=2026-03-10/
      part-0001.snappy.parquet
      _SUCCESS
```

See `context/stacks/parquet.md` for partition key selection rules.

## Read Path Configuration

### DuckDB

```python
import duckdb

conn = duckdb.connect()
conn.execute("INSTALL httpfs; LOAD httpfs;")
conn.execute(f"""
    SET s3_endpoint='{minio_endpoint}';
    SET s3_access_key_id='{access_key}';
    SET s3_secret_access_key='{secret_key}';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

result = conn.execute("""
    SELECT tenant_id, COUNT(*) AS row_count
    FROM read_parquet('s3://dev-report-data/reports/**/*.parquet', hive_partitioning=true)
    WHERE tenant_id = 'acme'
    GROUP BY tenant_id
""").fetchall()
```

### Polars

```python
import polars as pl
import s3fs

fs = s3fs.S3FileSystem(
    key=access_key,
    secret=secret_key,
    endpoint_url=minio_endpoint,
    use_ssl=False,
)

df = pl.scan_parquet(
    "s3://dev-report-data/reports/**/*.parquet",
    storage_options={
        "key": access_key,
        "secret": secret_key,
        "endpoint_url": minio_endpoint,
        "use_ssl": False,
    },
).filter(pl.col("tenant_id") == "acme").collect()
```

### Trino

Configure the Hive connector to point at MinIO. Set `hive.s3.endpoint` and `hive.s3.path-style-access=true` in the catalog properties file. See `context/stacks/trino.md` for catalog configuration detail.

## Retention and Deletion

- Delete old partition prefixes rather than individual files. A single `s3.delete_objects()` call on a partition prefix is more efficient than listing and deleting individual files.
- If the deployment supports it, configure a bucket lifecycle policy to expire objects after a retention window rather than running application-level cleanup on each write cycle.
- Never delete the current partition prefix while a write is in progress — use the staging prefix pattern so the current final partition is always consistent.

## Interaction With Existing Stacks

- `parquet-minio` is the **write side**; `duckdb-trino-polars` is the **read side**.
- When both are present in a repo, load both packs.
- `parquet-minio` does not replace `duckdb-trino-polars`; it extends it by answering "how does data get into the bucket in the first place?"

## Change Surfaces To Watch

- **Schema changes at the writer**: any field add, remove, or reorder breaks readers that pin the Arrow schema. Treat the Parquet schema as a stable API.
- **Partition key changes**: changing partition key names (e.g., `date` to `event_date`) breaks Hive-style partition discovery without a data migration.
- **Credential rotation**: MinIO credentials are read from environment variables. Ensure `docker-compose.test.yml` and application config use the same variable names.
- **Staging prefix leaks**: if the writer crashes between the staging write and the rename, the `_staging/` prefix accumulates orphaned files. Add a cleanup step to the test teardown and to the production write path.

## Testing Expectations

- Run a real MinIO container in `docker-compose.test.yml`; do not mock the object store.
- Write a small deterministic dataset, read it back with DuckDB or Polars, assert row count and one column value.
- Verify the staging-to-final rename by asserting no objects remain under `_staging/` after a successful write.
- Verify partition discovery: read with `hive_partitioning=true` and filter by partition key; assert only the expected partition rows are returned.

## Common Assistant Mistakes

- Skipping the staging prefix pattern and writing directly to the final key (partial writes become visible to readers).
- Forgetting to create the test bucket in integration test setup (the first write will fail with a bucket-not-found error).
- Using virtual-hosted-style URL addressing for MinIO instead of path-style.
- Reading all partitions when only one is needed (missing `WHERE tenant_id = ...` in DuckDB or Polars filter pushdown).
- Treating `parquet-minio` as a standalone pack and forgetting to load `duckdb-trino-polars` for the read-path guidance.
