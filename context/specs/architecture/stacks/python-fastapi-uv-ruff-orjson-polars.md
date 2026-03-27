---
acb_origin: canonical
acb_source_path: context/specs/architecture/stacks/python-fastapi-uv-ruff-orjson-polars.md
acb_role: architecture
acb_stacks: [python-fastapi-uv-ruff-orjson-polars]
acb_version: 1
---

## FastAPI + uv + Ruff + orjson + Polars Constraints

Keep FastAPI route modules thin. Polars shaping should live in service or data modules, not inside route handlers. Serialization should be explicit at the boundary so JSON shape stays stable.

Validation should prefer app-factory or route-level proof plus one storage-backed round-trip when persistence exists.
