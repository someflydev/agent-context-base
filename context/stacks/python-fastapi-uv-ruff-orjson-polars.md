# Python: FastAPI + uv + Ruff + orjson + Polars

Use this pack for lightweight to medium API services and data-aware backend repos built around modern Python tooling.

## Typical Repo Surface

- `pyproject.toml`
- `uv.lock`
- `src/<app_name>/main.py`
- `src/<app_name>/api/`
- `src/<app_name>/services/`
- `src/<app_name>/storage/`
- `tests/smoke/`
- `tests/integration/`

## Common Change Surfaces

- router definitions
- request and response models
- service-layer logic
- Polars-based transforms
- storage adapters
- settings and environment parsing

## Testing Expectations

- smoke test app boot plus one representative route
- integration tests against Docker-backed test infra when routes touch PostgreSQL, Redis, MongoDB, search, or vector storage
- keep Polars transforms covered by focused tests if they carry business logic

## Common Assistant Mistakes

- centering Starlette instead of FastAPI
- putting all logic directly in route handlers
- defaulting to standard `json` instead of `orjson` where the repo already uses it
- treating database-backed endpoints as unit-test-only changes

