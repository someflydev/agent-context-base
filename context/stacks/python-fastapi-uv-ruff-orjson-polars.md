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

## Tool Setup

One-time setup (run once when cloning or initializing the repo):

```bash
uv venv --python 3.12 .venv_tools    # match the version in requires-python; default 3.12
uv pip install --python .venv_tools/bin/python pytest httpx pytest-asyncio
```

To add Playwright for e2e tests:

```bash
uv pip install --python .venv_tools/bin/python pytest-playwright playwright
.venv_tools/bin/playwright install chromium
```

Running tests:

```bash
.venv_tools/bin/pytest tests/unit/
.venv_tools/bin/pytest tests/integration/
.venv_tools/bin/pytest tests/e2e/          # if playwright is present
```

Never use `python -m pytest`, bare `pytest`, `pip install`, or `source .venv_tools/bin/activate`.
Always use explicit `.venv_tools/bin/` paths. See `context/doctrine/tool-invocation-discipline.md`.

## Common Assistant Mistakes

- centering Starlette instead of FastAPI
- putting all logic directly in route handlers
- defaulting to standard `json` instead of `orjson` where the repo already uses it
- treating database-backed endpoints as unit-test-only changes

## ML and Data Science Context

When the repo adds ML capability (classification, regression, recommendation, clustering, embedding, or time series forecasting), the stack expands. Load the full library guidance from `context/doctrine/python-ml-library-selection.md`.

Quick reference for the most common cases:
- Tabular ML (classification, regression, feature pipelines): scikit-learn + Polars data layer
- Gradient-boosted trees on structured data: XGBoost or LightGBM (drop-in sklearn API)
- Semantic embeddings for search or RAG: sentence-transformers
- Statistical inference with p-values: statsmodels
- Array math or custom metrics: numpy
- Statistical tests (t-test, ANOVA, chi-squared): scipy.stats

The Polars data layer does not change when ML is added. Polars handles data processing; sklearn/XGBoost/LightGBM handle model training; conversion happens at the model boundary:

```python
X = df.select(feature_columns).to_numpy()
```

## Common ML Mistakes In This Stack

- Adding pandas as a data processing layer when Polars already handles it.
- Doing ETL transforms inside sklearn ColumnTransformer — use Polars for ETL.
- Using sklearn.GradientBoostingClassifier on tabular data — prefer XGBoost or LightGBM.
- Converting the full DataFrame to pandas before sklearn — convert only feature columns to numpy.
- Adding the full transformers library for an embedding use case — sentence-transformers is sufficient.

Read `context/doctrine/python-ml-library-selection.md` before any ML feature implementation.
