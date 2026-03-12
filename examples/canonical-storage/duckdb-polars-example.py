from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl


DATABASE_PATH = Path("docker/volumes/dev/warehouse/analytics.duckdb")


def load_runs() -> pl.DataFrame:
    with duckdb.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            create table if not exists report_runs (
                tenant_id text,
                report_id text,
                total_events integer
            )
            """
        )
        connection.execute(
            """
            insert into report_runs values
                ('acme', 'daily-signups', 42),
                ('globex', 'daily-signups', 11)
            """
        )
        return pl.read_database(
            """
            select tenant_id, report_id, total_events
            from report_runs
            order by total_events desc
            """,
            connection=connection,
        )


if __name__ == "__main__":
    print(load_runs())

