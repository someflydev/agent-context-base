"""
Parquet + MinIO write-and-read-back example.

Verification level: structure-verified
No live MinIO dependency is required to import this module. The write_dataset()
and read_back() functions can be run against a real MinIO container or a local
filesystem path by changing the S3 credentials and endpoint env vars.

Follow-on: add a docker-compose harness under verification/scenarios/minio_parquet_min_app/
to raise this to smoke-verified.
"""

from __future__ import annotations

import io
import os
import uuid
from datetime import date, datetime, timezone

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.client import Config

# ---------------------------------------------------------------------------
# Schema — pinned explicitly; never inferred from data
# ---------------------------------------------------------------------------

SCHEMA = pa.schema(
    [
        pa.field("tenant_id", pa.string(), nullable=False),
        pa.field("report_id", pa.string(), nullable=False),
        pa.field("request_at", pa.timestamp("us", tz="UTC"), nullable=False),
        pa.field("response_status", pa.int16(), nullable=False),
        pa.field("response_time_ms", pa.int32(), nullable=True),
        pa.field("schema_version", pa.int8(), nullable=False),
    ]
)

SCHEMA_VERSION: int = 1

# ---------------------------------------------------------------------------
# Sample dataset — two tenants, two dates, ten rows total
# ---------------------------------------------------------------------------

SAMPLE_ROWS = [
    # tenant_id,   report_id,         request_at (UTC),              status, rt_ms
    ("acme", "daily-signups", datetime(2026, 3, 10, 8, 0, 0, tzinfo=timezone.utc), 200, 142),
    ("acme", "daily-signups", datetime(2026, 3, 10, 8, 1, 0, tzinfo=timezone.utc), 200, 98),
    ("acme", "daily-signups", datetime(2026, 3, 10, 8, 2, 0, tzinfo=timezone.utc), 500, 3100),
    ("acme", "daily-signups", datetime(2026, 3, 11, 9, 0, 0, tzinfo=timezone.utc), 200, 110),
    ("acme", "daily-signups", datetime(2026, 3, 11, 9, 1, 0, tzinfo=timezone.utc), 404, 55),
    ("globex", "weekly-revenue", datetime(2026, 3, 10, 12, 0, 0, tzinfo=timezone.utc), 200, 310),
    ("globex", "weekly-revenue", datetime(2026, 3, 10, 12, 1, 0, tzinfo=timezone.utc), 200, 287),
    ("globex", "weekly-revenue", datetime(2026, 3, 11, 13, 0, 0, tzinfo=timezone.utc), 200, 401),
    ("globex", "weekly-revenue", datetime(2026, 3, 11, 13, 1, 0, tzinfo=timezone.utc), 500, 2100),
    ("globex", "weekly-revenue", datetime(2026, 3, 11, 13, 2, 0, tzinfo=timezone.utc), 200, 195),
]


# ---------------------------------------------------------------------------
# MinIO client
# ---------------------------------------------------------------------------

def _make_s3_client() -> "boto3.client":
    """Build a boto3 S3 client from environment variables.

    Required env vars:
        MINIO_ACCESS_KEY  — access key
        MINIO_SECRET_KEY  — secret key
        MINIO_ENDPOINT    — e.g. http://localhost:9000
    """
    return boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",  # MinIO ignores this but boto3 requires it
    )


# ---------------------------------------------------------------------------
# Partition helpers
# ---------------------------------------------------------------------------

def _partition_key(tenant_id: str, event_date: date) -> str:
    """Return the Hive-style partition path component for one tenant+date."""
    return f"tenant_id={tenant_id}/date={event_date.isoformat()}"


def _object_key(tenant_id: str, event_date: date, sequence: int) -> str:
    """Return the final object key for a partition file."""
    return f"reports/{_partition_key(tenant_id, event_date)}/part-{sequence:04d}.snappy.parquet"


def _staging_key(final_key: str) -> str:
    """Return the staging key for a given final key."""
    return f"_staging/{final_key}"


# ---------------------------------------------------------------------------
# Write path
# ---------------------------------------------------------------------------

def _build_table_for_partition(
    tenant_id: str, event_date: date, rows: list[tuple]
) -> pa.Table:
    """Build a PyArrow Table for one tenant+date partition."""
    matching = [r for r in rows if r[0] == tenant_id and r[2].date() == event_date]
    if not matching:
        raise ValueError(f"No rows for tenant={tenant_id} date={event_date}")

    return pa.table(
        {
            "tenant_id": [r[0] for r in matching],
            "report_id": [r[1] for r in matching],
            "request_at": pa.array([r[2] for r in matching], type=pa.timestamp("us", tz="UTC")),
            "response_status": pa.array([r[3] for r in matching], type=pa.int16()),
            "response_time_ms": pa.array([r[4] for r in matching], type=pa.int32()),
            "schema_version": pa.array([SCHEMA_VERSION] * len(matching), type=pa.int8()),
        },
        schema=SCHEMA,
    )


def _write_table_to_bytes(table: pa.Table) -> bytes:
    """Serialise a PyArrow Table to Parquet bytes (Snappy compressed)."""
    buf = io.BytesIO()
    pq.write_table(
        table,
        buf,
        compression="snappy",
        use_dictionary=True,
        row_group_size=1024 * 1024,  # 1 MB for this small example
    )
    return buf.getvalue()


def write_dataset(bucket: str, rows: list[tuple] | None = None) -> list[str]:
    """Write the sample dataset to MinIO using the staging-prefix pattern.

    Returns the list of final object keys written.

    Args:
        bucket: target MinIO bucket (must already exist)
        rows:   dataset rows; defaults to SAMPLE_ROWS

    Write sequence per partition:
        1. Write Parquet bytes to _staging/<final_key>
        2. Copy staging object to final key
        3. Delete staging object
    """
    if rows is None:
        rows = SAMPLE_ROWS

    s3 = _make_s3_client()

    # Collect distinct (tenant_id, date) partitions
    partitions: set[tuple[str, date]] = {(r[0], r[2].date()) for r in rows}

    written_keys: list[str] = []
    sequence = 1

    for tenant_id, event_date in sorted(partitions):
        table = _build_table_for_partition(tenant_id, event_date, rows)
        parquet_bytes = _write_table_to_bytes(table)

        final_key = _object_key(tenant_id, event_date, sequence)
        staging = _staging_key(final_key)

        # Step 1: write to staging
        s3.put_object(Bucket=bucket, Key=staging, Body=parquet_bytes)

        # Step 2: copy to final path (atomic at the object level)
        s3.copy_object(
            Bucket=bucket,
            CopySource={"Bucket": bucket, "Key": staging},
            Key=final_key,
        )

        # Step 3: delete staging object
        s3.delete_object(Bucket=bucket, Key=staging)

        written_keys.append(final_key)
        sequence += 1

    return written_keys


# ---------------------------------------------------------------------------
# Read-back (DuckDB)
# ---------------------------------------------------------------------------

def read_back(bucket: str) -> int:
    """Read back the dataset with DuckDB and return the total row count.

    Requires the httpfs DuckDB extension. If the extension is not installed,
    DuckDB will prompt to install it on the first run.

    Returns:
        Total row count across all partitions in the bucket.
    """
    import duckdb  # type: ignore[import]

    endpoint = os.environ["MINIO_ENDPOINT"].replace("http://", "").replace("https://", "")
    use_ssl = os.environ["MINIO_ENDPOINT"].startswith("https")

    conn = duckdb.connect()
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute(f"""
        SET s3_endpoint='{endpoint}';
        SET s3_access_key_id='{os.environ["MINIO_ACCESS_KEY"]}';
        SET s3_secret_access_key='{os.environ["MINIO_SECRET_KEY"]}';
        SET s3_use_ssl={'true' if use_ssl else 'false'};
        SET s3_url_style='path';
    """)

    result = conn.execute(f"""
        SELECT COUNT(*) AS total
        FROM read_parquet(
            's3://{bucket}/reports/**/*.parquet',
            hive_partitioning = true
        )
    """).fetchone()

    conn.close()
    return result[0]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    """Write the sample dataset and assert the row count on read-back.

    Requires a running MinIO instance and the following env vars:
        MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT

    The target bucket must exist before running this script.
    Example bucket name: test-report-data
    """
    bucket = os.environ.get("MINIO_BUCKET", "test-report-data")

    print(f"Writing dataset to bucket '{bucket}' ...")
    keys = write_dataset(bucket)
    print(f"Wrote {len(keys)} partition file(s):")
    for k in keys:
        print(f"  {k}")

    print("Reading back with DuckDB ...")
    total = read_back(bucket)
    expected = len(SAMPLE_ROWS)
    assert total == expected, f"Row count mismatch: expected {expected}, got {total}"
    print(f"OK — {total} rows verified.")


if __name__ == "__main__":
    main()
