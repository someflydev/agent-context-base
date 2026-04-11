from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from models import SyncRun, WorkspaceConfig


FIXTURES = (
    Path(__file__).resolve().parents[2]
    / "domain"
    / "fixtures"
)


def _load(name: str) -> object:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def main() -> None:
    workspace_schema = WorkspaceConfig.model_json_schema()
    sync_run_schema = SyncRun.model_json_schema()

    print(json.dumps(workspace_schema, indent=2))
    print(json.dumps(sync_run_schema, indent=2))

    json.loads(json.dumps(workspace_schema))
    json.loads(json.dumps(sync_run_schema))

    validate(_load("valid/workspace_config_full.json"), workspace_schema)
    try:
        validate(_load("invalid/workspace_config_bad_slug.json"), workspace_schema)
    except Exception as exc:
        print(f"drift check rejected invalid workspace fixture: {exc.__class__.__name__}")
    else:
        raise SystemExit("invalid fixture unexpectedly passed exported JSON Schema")

    print("schema export and drift checks passed")


if __name__ == "__main__":
    main()
