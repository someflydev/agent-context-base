# FastAPI + uv Runtime Example

Minimal runtime bundle for the `python-fastapi-uv-ruff` stack. Managed with uv,
linted with ruff. No polars, no orjson.

Routes:

- `GET /healthz`
- `GET /api/reports/{tenant_id}`
- `GET /fragments/report-card/{tenant_id}`
- `GET /data/chart/{metric}`

Verification level: smoke-verified
Harness: fastapi_uv_min_app
Last verified by: verification/examples/python/test_fastapi_examples.py

Local dev:

    uv sync
    uvicorn app:app --reload
