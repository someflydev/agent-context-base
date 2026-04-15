# Analytics Workbench

A FastAPI + HTMX + Tailwind + Plotly canonical example for server-rendered visualization.

## Running

```bash
uv pip install -e .[dev]
uvicorn src.analytics_workbench.main:app --reload
```

## Testing

```bash
pytest tests/ -v
```
