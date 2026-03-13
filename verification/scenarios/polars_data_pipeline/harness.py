from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from verification.helpers import REPO_ROOT, load_python_module, python_data_stub_modules


STORAGE_EXAMPLE = REPO_ROOT / "examples/canonical-storage/duckdb-polars-example.py"
SEED_EXAMPLE = REPO_ROOT / "examples/canonical-seed-data/polars-seed-data-example.py"


@contextlib.contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def run_storage_scenario() -> list[dict[str, Any]]:
    module = load_python_module(
        STORAGE_EXAMPLE,
        module_name="verification.scenarios.polars_data_pipeline.storage",
        stub_modules=python_data_stub_modules(),
    )
    frame = module.load_runs()
    return frame.to_dicts()


def run_seed_scenario(*, app_env: str) -> dict[str, Any]:
    module = load_python_module(
        SEED_EXAMPLE,
        module_name=f"verification.scenarios.polars_data_pipeline.seed.{app_env}",
        stub_modules=python_data_stub_modules(),
    )
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        previous_env = os.environ.get("APP_ENV")
        os.environ["APP_ENV"] = app_env
        try:
            with working_directory(root):
                module.main()
                target = root / module.seed_root() / "report_runs.parquet"
        finally:
            if previous_env is None:
                os.environ.pop("APP_ENV", None)
            else:
                os.environ["APP_ENV"] = previous_env

        return {
            "target": target.relative_to(root).as_posix(),
            "rows": json.loads(target.read_text(encoding="utf-8")),
        }
