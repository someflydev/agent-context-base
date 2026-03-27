---
acb_origin: canonical
acb_source_path: context/validation/stacks/python-fastapi-uv-ruff-orjson-polars.md
acb_role: validation
acb_stacks: [python-fastapi-uv-ruff-orjson-polars]
acb_version: 1
---

## FastAPI Stack Validation

Prefer request-harness or app-factory proof for route contracts, then add one storage-backed integration check when the route depends on persistence or Polars shaping.

Typical commands:

- repo-local route smoke or integration command for the changed boundary
- `python -m unittest verification.examples.python.test_fastapi_examples -v` when validating canonical examples in the base repo
