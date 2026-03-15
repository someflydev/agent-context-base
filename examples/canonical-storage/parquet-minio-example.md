# Parquet + MinIO Example

**Verification level: structure-verified**
Harness: none (follow-on task: add `verification/scenarios/minio_parquet_min_app/` for smoke-verified coverage)
Last verified by: `verification/examples/data/test_storage_examples.py`

This example covers writing a partitioned Parquet dataset to MinIO and reading it back with DuckDB. It is the reference for the data-lake write path used alongside the `duckdb-trino-polars` read layer.

See `parquet-minio-example.py` for the runnable implementation.

---

## Bucket and Key Structure

Bucket: `dev-report-data` (dev) / `test-report-data` (test)

Object key schema:
```
reports/tenant_id=<tenant>/date=<YYYY-MM-DD>/part-<seq>.snappy.parquet
```

Example keys after a successful write:
```
reports/tenant_id=acme/date=2026-03-10/part-0001.snappy.parquet
reports/tenant_id=globex/date=2026-03-10/part-0001.snappy.parquet
```

Staging prefix during write:
```
_staging/reports/tenant_id=acme/date=2026-03-10/part-0001.snappy.parquet
```

The staging prefix is renamed to the final path after all parts flush successfully. This prevents downstream readers from discovering partial writes.

---

## Schema Pinning

Define the Arrow schema explicitly at module level. Never infer from the first batch.

```python
import pyarrow as pa

SCHEMA = pa.schema([
    pa.field("tenant_id",        pa.string(),                    nullable=False),
    pa.field("report_id",        pa.string(),                    nullable=False),
    pa.field("request_at",       pa.timestamp("us", tz="UTC"),   nullable=False),
    pa.field("response_status",  pa.int16(),                     nullable=False),
    pa.field("response_time_ms", pa.int32(),                     nullable=True),
    pa.field("schema_version",   pa.int8(),                      nullable=False),
])
```

Evolution rules:
- Add new fields with `nullable=True` and a default. Existing readers that pin this schema will skip the new column.
- Never remove or reorder existing fields.
- Increment `schema_version` when the shape changes materially.

---

## Write Path

### Environment Variables

```
MINIO_ACCESS_KEY=dev-access-key
MINIO_SECRET_KEY=dev-secret-key
MINIO_ENDPOINT=http://localhost:9000
```

Never hardcode credentials. In `docker-compose.test.yml`, define a separate set of test credentials and a separate named volume.

### Partition Naming

Hive-style partition directories — the read layer (DuckDB, Polars, Trino) discovers partitions by parsing directory names:

```
reports/
  tenant_id=acme/
    date=2026-03-10/
      part-0001.snappy.parquet
  tenant_id=globex/
    date=2026-03-10/
      part-0001.snappy.parquet
```

Partition key selection rules (from `context/stacks/parquet.md`):
- Partition by the most common filter dimension first — `tenant_id` for per-tenant queries.
- Avoid high-cardinality partition keys (UUID, raw timestamp).

### Staging Prefix Pattern

1. Write the Parquet file to `_staging/<final_key>`.
2. On success, copy the object from staging to the final key path.
3. Delete the staging object.
4. Optionally write a `_SUCCESS` marker if downstream consumers poll for completeness.

If the writer crashes between step 1 and step 2, the `_staging/` prefix contains orphaned files. Add a cleanup step in test teardown and in the production write startup path.

---

## Read Path (DuckDB)

```python
import duckdb, os

conn = duckdb.connect()
conn.execute("INSTALL httpfs; LOAD httpfs;")
conn.execute(f"""
    SET s3_endpoint='{os.environ["MINIO_ENDPOINT"].replace("http://", "")}';
    SET s3_access_key_id='{os.environ["MINIO_ACCESS_KEY"]}';
    SET s3_secret_access_key='{os.environ["MINIO_SECRET_KEY"]}';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

rows = conn.execute("""
    SELECT tenant_id, COUNT(*) AS row_count
    FROM read_parquet(
        's3://dev-report-data/reports/**/*.parquet',
        hive_partitioning = true
    )
    WHERE tenant_id = 'acme'
    GROUP BY tenant_id
""").fetchall()

assert rows[0][1] == 5, f"Expected 5 rows for acme, got {rows[0][1]}"
```

Key points:
- `SET s3_url_style='path'` is required for MinIO. Without it, DuckDB defaults to virtual-hosted-style addressing which fails on local MinIO.
- `hive_partitioning = true` enables partition pruning from the directory names.
- `SET s3_use_ssl=false` for local development without TLS.

---

## Docker Compose (test)

```yaml
services:
  minio-test:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: test-access-key
      MINIO_ROOT_PASSWORD: test-secret-key
    ports:
      - "19000:9000"
      - "19001:9001"
    volumes:
      - minio-test-data:/data

  minio-setup:
    image: minio/mc
    depends_on:
      - minio-test
    entrypoint: >
      /bin/sh -c "
        mc alias set local http://minio-test:9000 test-access-key test-secret-key;
        mc mb --ignore-existing local/test-report-data;
      "

volumes:
  minio-test-data:
```

Keep `minio-test-data` separate from the dev volume. Never share test and dev object store data.

---

## Follow-On Task

A `verification/scenarios/minio_parquet_min_app/` docker-compose harness would raise this example from structure-verified to smoke-verified. The harness would:
1. Start MinIO with the test credentials above.
2. Run `parquet-minio-example.py` write path.
3. Run the DuckDB read-back assertion.
4. Assert row count matches.

This is the recommended next step to increase trust without requiring changes to the example files.
