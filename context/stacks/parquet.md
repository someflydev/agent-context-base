# Parquet

Use this pack when a repo writes, reads, or partitions Parquet files as its primary analytical storage format. Parquet is a file-format discipline, not a database — load the appropriate read-layer pack (DuckDB, Polars, Trino) alongside this one when the query path also matters.

## When To Choose Parquet

- **Parquet** when the consumer is columnar: DuckDB, Polars, Spark, Trino. Columnar storage means only touched columns are read from disk; file-level metadata allows whole row groups to be skipped via predicate pushdown.
- **JSONL** when the consumer is a log processor, streaming pipeline, or document store that reads record by record.
- **Avro** when schema evolution across multiple producer/consumer pairs must be governed by a schema registry (Confluent, Glue). Avro carries the schema inside each file; the registry enforces compatibility.

Parquet does not self-govern schema evolution — the writer owns that responsibility.

## Typical Repo Surface

- `app/parquet/writer.py` or equivalent — Arrow schema definition, row group flush logic
- `app/parquet/reader.py` or equivalent — DuckDB/Polars scan entrypoint
- `scripts/write_parquet.py` — deterministic sample write for local testing
- `tests/integration/test_parquet_roundtrip.py` — write and read back with assertion on row count and column types
- `docker-compose.test.yml` — MinIO or local path mount for integration tests

## Schema Definition and Evolution

Pin the Arrow/PyArrow schema explicitly at module level. Never infer schema from the first batch — inference produces Silent type coercion when empty batches or nullable columns appear.

```python
import pyarrow as pa

SCHEMA = pa.schema([
    pa.field("tenant_id", pa.string(), nullable=False),
    pa.field("report_id", pa.string(), nullable=False),
    pa.field("request_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("response_status", pa.int16(), nullable=False),
    pa.field("response_time_ms", pa.int32(), nullable=True),
    pa.field("schema_version", pa.int8(), nullable=False),
])
```

Evolution rules:
- **Add** fields with a nullable default: existing readers skip the new column, new writers populate it.
- **Never remove or reorder** existing fields — readers that pin a schema will misalign columns.
- **Increment `schema_version`** when the shape changes materially; consumers can reject or adapt based on the version field.

## Partitioning Strategy

Partition by the most common filter dimension first. Hive convention: `<key>=<value>/` directory names.

```
data/
  tenant_id=acme/
    date=2026-03-10/
      part-0001.snappy.parquet
  tenant_id=globex/
    date=2026-03-10/
      part-0001.snappy.parquet
```

Rules:
- **First partition key** = the field used in every query's `WHERE` clause (typically `tenant_id`).
- **Second partition key** = the date or week bucket.
- **Avoid high-cardinality partition keys**: do not partition by UUID, raw timestamp, or any field with more than a few hundred distinct values. Each partition directory adds file-system overhead; a directory with one row per partition defeats row group efficiency.
- Keep partition key values lowercase and URL-safe; readers reconstruct them from directory names.

## Compression Codec Selection

| Codec | Decode speed | Ratio | When to use |
|---|---|---|---|
| Snappy | Fast | Moderate | Latency-sensitive interactive reads |
| Zstandard (zstd) | Moderate | High | Cold storage, infrequent reads |
| Uncompressed | Fastest | None | Avoid for anything stored longer than a day |

Default: Snappy for actively queried data, Zstandard for archival partitions.

## Row Group Sizing

- **128 MB to 512 MB** per row group for large analytical workloads. Smaller row groups produce more file-level metadata and hurt scan performance.
- **8 MB to 64 MB** for streaming or incremental writes where memory pressure is a concern.
- Never write one row group per row or one file per minute — the small-files problem causes disproportionate metadata overhead for DuckDB, Trino, and S3-compatible object stores.

## Change Surfaces To Watch

- **Schema drift**: any change to field name, type, or order breaks downstream readers that pin a schema. Track schema changes in a constants file, not ad-hoc.
- **Partition layout changes**: renaming partition keys breaks Hive-style discovery in Trino/Polars. Treat partition key names as a stable API.
- **Codec mismatch**: mixing Snappy and Zstandard parts in the same dataset forces readers to detect and switch codecs per file. Pick one per dataset.
- **Row group size regressions**: verify row group count after any write refactor; a regression to one-file-per-record is silent at write time but catastrophic at query time.

## Testing Expectations

- Write a small deterministic dataset (two or more partition keys, ten or more rows) and read it back.
- Assert row count, column types, and at least one partition key value match the expected output.
- For schema evolution: write v1, write v2 with an added nullable column, assert both can be read by the same reader without error.
- Do not test Parquet correctness through mocks — write real files to a temp directory or a test MinIO bucket.

## Common Assistant Mistakes

- Writing one Parquet file per row or one file per incoming event (small-files problem).
- Inferring schema from the first batch rather than defining it explicitly at module level.
- Mixing compressed and uncompressed files in the same partition directory.
- Partitioning by UUID or raw timestamp instead of a stable, low-cardinality key.
- Removing or reordering existing fields during schema evolution instead of only appending nullable fields.
