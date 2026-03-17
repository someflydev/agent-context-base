"""
DuckDB + Parquet local round-trip example.

Verification level: structure-verified
No object store or network dependency. All files are written to local disk
under DATA_DIR. The write_fixtures() function creates real Parquet files;
query() scans them with DuckDB using hive partition pruning; the result is
returned as a Polars DataFrame.

Follow-on: add a verification harness under
verification/scenarios/duckdb_parquet_min_app/ to raise this to
smoke-verified.

See duckdb-parquet-example.md for design rationale, connection mode guidance,
and relationship to other storage examples.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq


# ---------------------------------------------------------------------------
# Schema — pinned explicitly at module level; never inferred from data.
# ---------------------------------------------------------------------------

SCHEMA = pa.schema([
    pa.field("tenant_id", pa.string(), nullable=False),
    pa.field("report_id", pa.string(), nullable=False),
    pa.field("event_count", pa.int32(), nullable=False),
    pa.field("schema_version", pa.int8(), nullable=False),
])

# ---------------------------------------------------------------------------
# Data directory — Hive-partitioned Parquet files live here.
# ---------------------------------------------------------------------------

DATA_DIR = Path("docker/volumes/dev/parquet/reports")


# ---------------------------------------------------------------------------
# Write path — PyArrow with pinned schema, one file per tenant partition.
# ---------------------------------------------------------------------------

def write_fixtures(data_dir: Path = DATA_DIR) -> Path:
    """Write deterministic Parquet fixtures to Hive-partitioned directories.

    Creates two partition directories:
        <data_dir>/tenant_id=acme/date=2026-03-10/
        <data_dir>/tenant_id=globex/date=2026-03-10/

    Writes one Parquet file per tenant. Returns data_dir so the caller can
    pass it directly to query().

    PyArrow is the canonical write path (not DuckDB COPY TO) because:
    - The schema is explicit and pinned in SCHEMA above.
    - Schema inference from the first batch is avoided.
    - Hive-style partition directories are created explicitly by the writer.
    """
    acme_dir = data_dir / "tenant_id=acme" / "date=2026-03-10"
    globex_dir = data_dir / "tenant_id=globex" / "date=2026-03-10"

    # Must create directories before calling pq.write_table() — PyArrow raises
    # FileNotFoundError if the target directory does not exist.
    acme_dir.mkdir(parents=True, exist_ok=True)
    globex_dir.mkdir(parents=True, exist_ok=True)

    acme_table = pa.table(
        {
            "tenant_id": ["acme", "acme"],
            "report_id": ["r-001", "r-002"],
            "event_count": pa.array([42, 17], type=pa.int32()),
            "schema_version": pa.array([1, 1], type=pa.int8()),
        },
        schema=SCHEMA,
    )

    globex_table = pa.table(
        {
            "tenant_id": ["globex"],
            "report_id": ["r-003"],
            "event_count": pa.array([11], type=pa.int32()),
            "schema_version": pa.array([1], type=pa.int8()),
        },
        schema=SCHEMA,
    )

    pq.write_table(
        acme_table,
        acme_dir / "part-0001.snappy.parquet",
        compression="snappy",
        row_group_size=131072,
    )
    pq.write_table(
        globex_table,
        globex_dir / "part-0001.snappy.parquet",
        compression="snappy",
        row_group_size=131072,
    )

    return data_dir


# ---------------------------------------------------------------------------
# Query path — DuckDB read_parquet() with hive_partitioning, Polars output.
# ---------------------------------------------------------------------------

def query(data_dir: Path, tenant_filter: str = "acme") -> pl.DataFrame:
    """Query partitioned Parquet files with DuckDB and return a Polars DataFrame.

    Uses an in-memory DuckDB connection (duckdb.connect() with no path
    argument) — no .duckdb file is created on disk. This is correct for
    read-only Parquet scans. Only use a file-backed connection when caching
    query results into persistent DuckDB tables for repeated queries.

    hive_partitioning=true causes DuckDB to read the tenant_id and date values
    from directory names and inject them as virtual columns. The WHERE clause
    on tenant_id is pushed down to directory selection — directories that don't
    match the predicate are skipped entirely before DuckDB opens any files.

    pl.from_arrow(rel.arrow()) converts the DuckDB relation to a Polars
    DataFrame via the Arrow IPC format. This is preferred over
    pl.read_database() because it avoids a second SQL string round-trip and
    preserves the Arrow schema exactly.
    """
    glob_path = str(data_dir / "**" / "*.parquet")

    conn = duckdb.connect()
    rel = conn.sql(f"""
        SELECT tenant_id, report_id, event_count
        FROM read_parquet('{glob_path}', hive_partitioning=true)
        WHERE tenant_id = '{tenant_filter}'
        ORDER BY event_count DESC
    """)
    return pl.from_arrow(rel.arrow())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # write_fixtures() creates real Parquet files on disk under DATA_DIR;
    # query() scans them with DuckDB hive partition pruning and returns
    # only the rows matching the tenant filter;
    # the result is a Polars DataFrame ready for downstream transforms.
    data_dir = write_fixtures()
    df = query(data_dir)
    print(df)
