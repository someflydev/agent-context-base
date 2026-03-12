# FastAPI Endpoint Example

This example shows the preferred FastAPI route shape for a small analytics endpoint:

- keep transport concerns in the route
- keep Polars shaping in a service boundary
- make dependency wiring explicit
- return a response model instead of leaking raw frame rows

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/fastapi-endpoint-example.py`
- `examples/canonical-smoke-tests/fastapi-smoke-test-example.py`
- `examples/canonical-integration-tests/fastapi-db-integration-test-example.py`
