# Python FastAPI Polars HTMX Plotly

Purpose: preferred Python web and data stack.

Typical paths:

- `app/routes/`
- `app/services/`
- `app/templates/`
- `tests/`

Conventions:

- use `uv` for environment and dependency management
- keep routes thin
- use Polars for table-heavy transformations
- keep HTMX partials explicit
- serialize JSON predictably

Testing:

- `pytest` plus smoke tests
- real Docker-backed integration tests for persistence or service boundaries
