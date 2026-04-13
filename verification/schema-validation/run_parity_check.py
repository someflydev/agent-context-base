#!/usr/bin/env python3
"""
Parity matrix runner for the schema-validation arc.

Checks the universally-required PARITY.md behaviors against the Python
implementations that can run without a separate language toolchain.

Only the Python examples are executed here. Go, Rust, Kotlin, Ruby, and Elixir
parity checks remain in their toolchain-specific runners under
verification/schema-validation/. Missing Python dependencies are reported as
SKIP instead of FAIL so the scope boundary stays explicit.

Exit code 0: all executed parity checks passed, with optional SKIPs.
Exit code 1: one or more executed parity checks failed.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = (
    REPO_ROOT / "examples" / "canonical-schema-validation" / "domain" / "fixtures"
)
VALID_FIXTURES = sorted((FIXTURES_DIR / "valid").glob("*.json"))
INVALID_FIXTURES = sorted((FIXTURES_DIR / "invalid").glob("*.json"))

PYDANTIC_MODELS_PATH = (
    REPO_ROOT
    / "examples"
    / "canonical-schema-validation"
    / "python"
    / "pydantic"
    / "models.py"
)
MARSHMALLOW_SCHEMAS_PATH = (
    REPO_ROOT
    / "examples"
    / "canonical-schema-validation"
    / "python"
    / "marshmallow"
    / "schemas.py"
)

MODEL_KEY_BY_PREFIX = {
    "workspace_config": "workspace_config",
    "sync_run": "sync_run",
    "webhook_payload": "webhook_payload",
    "ingestion_source": "ingestion_source",
    "review_request": "review_request",
}

results: list[tuple[str, str, str]] = []


def load_fixture(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def model_key_for_fixture(path: Path) -> str | None:
    for prefix, key in MODEL_KEY_BY_PREFIX.items():
        if path.stem.startswith(prefix):
            return key
    return None


def load_module(module_name: str, module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to build module spec for {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(implementation: str, status: str, message: str) -> None:
    results.append((implementation, status, message))


def check_pydantic() -> None:
    try:
        module = load_module("prompt118_pydantic_models", PYDANTIC_MODELS_PATH)
    except Exception as exc:
        record("pydantic", "SKIP", f"not importable: {exc}")
        return

    model_map = {
        "workspace_config": module.WorkspaceConfig,
        "sync_run": module.SyncRun,
        "webhook_payload": module.WebhookPayload,
        "ingestion_source": module.IngestionSource,
        "review_request": module.ReviewRequest,
    }
    validation_error = module.ValidationError

    for fixture_path in VALID_FIXTURES:
        model_key = model_key_for_fixture(fixture_path)
        if model_key is None:
            continue
        try:
            model_map[model_key].model_validate(load_fixture(fixture_path))
        except Exception as exc:
            record("pydantic", "FAIL", f"valid/{fixture_path.name} rejected: {exc}")
        else:
            record("pydantic", "PASS", f"valid/{fixture_path.name}")

    for fixture_path in INVALID_FIXTURES:
        model_key = model_key_for_fixture(fixture_path)
        if model_key is None:
            continue
        try:
            model_map[model_key].model_validate(load_fixture(fixture_path))
        except validation_error:
            record("pydantic", "PASS", f"invalid/{fixture_path.name} rejected")
        except Exception as exc:
            record(
                "pydantic",
                "FAIL",
                f"invalid/{fixture_path.name} raised unexpected error: {exc}",
            )
        else:
            record(
                "pydantic",
                "FAIL",
                f"invalid/{fixture_path.name} accepted (should be rejected)",
            )


def check_marshmallow() -> None:
    try:
        module = load_module("prompt118_marshmallow_schemas", MARSHMALLOW_SCHEMAS_PATH)
    except Exception as exc:
        record("marshmallow", "SKIP", f"not importable: {exc}")
        return

    schema_map = {
        "workspace_config": module.WorkspaceConfigSchema,
        "sync_run": module.SyncRunSchema,
        "webhook_payload": module.WebhookPayloadSchema,
        "ingestion_source": module.IngestionSourceSchema,
        "review_request": module.ReviewRequestSchema,
    }
    validation_error = module.ValidationError

    for fixture_path in VALID_FIXTURES:
        model_key = model_key_for_fixture(fixture_path)
        if model_key is None:
            continue
        schema = schema_map[model_key]()
        try:
            schema.load(load_fixture(fixture_path))
        except Exception as exc:
            record("marshmallow", "FAIL", f"valid/{fixture_path.name} rejected: {exc}")
        else:
            record("marshmallow", "PASS", f"valid/{fixture_path.name}")

    for fixture_path in INVALID_FIXTURES:
        model_key = model_key_for_fixture(fixture_path)
        if model_key is None:
            continue
        schema = schema_map[model_key]()
        try:
            schema.load(load_fixture(fixture_path))
        except validation_error:
            record("marshmallow", "PASS", f"invalid/{fixture_path.name} rejected")
        except Exception as exc:
            record(
                "marshmallow",
                "FAIL",
                f"invalid/{fixture_path.name} raised unexpected error: {exc}",
            )
        else:
            record(
                "marshmallow",
                "FAIL",
                f"invalid/{fixture_path.name} accepted (should be rejected)",
            )


def main() -> int:
    check_pydantic()
    check_marshmallow()

    passes = [row for row in results if row[1] == "PASS"]
    fails = [row for row in results if row[1] == "FAIL"]
    skips = [row for row in results if row[1] == "SKIP"]

    print(
        f"\nParity Check Results: {len(passes)} PASS, "
        f"{len(fails)} FAIL, {len(skips)} SKIP\n"
    )
    for implementation, status, message in results:
        print(f"[{status}] {implementation}: {message}")

    if fails:
        print(f"\n{len(fails)} parity check(s) FAILED.")
        return 1

    print(
        "\nAll executed parity checks PASSED. "
        "Toolchain-scoped implementations may appear as SKIP."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
