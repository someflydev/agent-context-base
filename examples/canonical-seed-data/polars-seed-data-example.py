from __future__ import annotations

import os
from pathlib import Path

import polars as pl


def seed_root() -> Path:
    app_env = os.environ.get("APP_ENV", "dev")
    if app_env == "test":
        return Path("docker/volumes/test/warehouse")
    return Path("docker/volumes/dev/warehouse")


def build_seed_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "tenant_id": ["acme", "acme", "globex"],
            "report_id": ["daily-signups", "failed-payments", "daily-signups"],
            "total_events": [42, 3, 11],
            "captured_at": [
                "2026-03-01T00:00:00Z",
                "2026-03-01T00:05:00Z",
                "2026-03-01T00:00:00Z",
            ],
        }
    )


def main() -> None:
    root = seed_root()
    root.mkdir(parents=True, exist_ok=True)
    target = root / "report_runs.parquet"
    build_seed_frame().write_parquet(target)
    print(f"Seeded {target}")


if __name__ == "__main__":
    main()

