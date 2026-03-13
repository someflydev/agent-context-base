from __future__ import annotations

import ast
import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.polars_data_pipeline.harness import run_seed_scenario, run_storage_scenario


STORAGE_EXAMPLE = REPO_ROOT / "examples/canonical-storage/duckdb-polars-example.py"
SEED_EXAMPLE = REPO_ROOT / "examples/canonical-seed-data/polars-seed-data-example.py"


class PolarsExampleTests(unittest.TestCase):
    def test_storage_example_parses(self) -> None:
        ast.parse(STORAGE_EXAMPLE.read_text(encoding="utf-8"))

    def test_seed_example_parses(self) -> None:
        ast.parse(SEED_EXAMPLE.read_text(encoding="utf-8"))

    def test_storage_harness_returns_deterministic_order(self) -> None:
        rows = run_storage_scenario()
        self.assertEqual([row["total_events"] for row in rows], [42, 11])

    def test_seed_harness_writes_isolated_paths(self) -> None:
        dev = run_seed_scenario(app_env="dev")
        test = run_seed_scenario(app_env="test")
        self.assertEqual(dev["target"], "docker/volumes/dev/warehouse/report_runs.parquet")
        self.assertEqual(test["target"], "docker/volumes/test/warehouse/report_runs.parquet")
        self.assertEqual(len(test["rows"]), 3)


if __name__ == "__main__":
    unittest.main()
