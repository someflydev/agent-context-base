# Python: FastAPI + uv + Ruff

Use this stack for lightweight API services that do not need columnar data processing. FastAPI handles routing, pydantic handles response models, uvicorn serves the app. uv manages dependencies. ruff handles linting. No heavy C extensions (no polars, no orjson).

## Typical Repo Surface

- `pyproject.toml`
- `uv.lock`
- `src/<app_name>/main.py`
- `src/<app_name>/api/`
- `src/<app_name>/services/`
- `tests/smoke/`
- `tests/integration/`

No `storage/` or data-transform layer.

## Common Change Surfaces

- router definitions
- request and response models (pydantic)
- service-layer logic (plain Python — list comprehensions, sorted(), dict operations)
- settings and environment parsing

## Testing Expectations

- smoke test: app boot plus one representative route
- integration tests against Docker-backed infra when routes touch PostgreSQL, Redis, or other external systems
- service logic covered by focused unit tests; no polars stub needed

## Common Assistant Mistakes

- reaching for polars for simple list filtering that plain Python handles fine
- importing orjson when FastAPI's built-in JSON serialization is sufficient
- defaulting to requirements.txt instead of pyproject.toml when the project already uses uv
- skipping ruff config in pyproject.toml
