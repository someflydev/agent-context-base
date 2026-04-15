# Python: FastAPI + Jinja2 + HTMX + Tailwind + Plotly

## Typical Repo Surface
- `app/main.py` — FastAPI application and routing
- `app/api/` — Route handlers for pages, partials, and JSON endpoints
- `app/services/` — Aggregation and query logic
- `app/charts/` — Plotly figure builders
- `app/templates/` — Jinja2 templates (pages and partials)
- `tests/` — pytest suites for routes, aggregation, and figures

## Key Libraries
- `fastapi`, `uvicorn` — HTTP framework and ASGI server
- `jinja2` — server-side HTML templates
- `plotly` — figure construction; `plotly.graph_objects` for full layout control
- `htmx` — partial page updates via HTML attributes (CDN or bundled)
- `tailwindcss` — utility-first styling (CDN script or compiled via CLI)
- `pandas` or `polars` — aggregation and data transforms
- `python-multipart` — form body parsing for HTMX form submissions
- `pytest`, `httpx` — route and fragment testing
- `playwright` (optional) — browser-level HTMX and filter interaction testing

## Figure Builder Pattern
```python
# app/charts/daily_trends.py
import plotly.graph_objects as go
from app.services.analytics import DailyTrendData

def build_daily_trend_figure(data: DailyTrendData) -> dict:
    # Build figure from aggregate data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.dates, y=data.values, name="Trend"))
    fig.update_layout(title="Daily Trend", xaxis_title="Date", yaxis_title="Count")
    # Return dict for testability without HTTP
    return fig.to_dict()

# app/api/charts.py
# Handler calls both and serializes: return JSONResponse(fig_dict)
```

## Jinja2 Fragment Pattern
```python
# Handler detects HTMX via header
if request.headers.get("HX-Request"):
    return templates.TemplateResponse("partials/chart_panel.html", context)
return templates.TemplateResponse("pages/dashboard.html", context)
```

## Tailwind + HTMX Filter Pattern
```html
<form hx-get="/api/partials/chart-panel" hx-target="#chart-panel" hx-swap="outerHTML">
  <select name="status" class="bg-white border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5">
    <option value="active">Active</option>
  </select>
  <!-- Active state buttons use filter-panel-rendering-rules.md classes -->
</form>
```

## Testing Expectations
- **Unit Tests:** Assert `plotly` figure structures (e.g., correct trace count and axis labels) independent of HTTP using `pytest`.
- **Integration Tests:** Use `httpx.AsyncClient` or `TestClient` to verify that chart endpoints and template fragment endpoints return 200 OK and correctly handle query params.
- **E2E Tests:** Ensure filters align with chart rendering via Playwright (if applicable).

## Common Assistant Mistakes
- Returning `figure.to_json()` directly from the builder instead of a testable `dict`.
- Building figures inside the FastAPI route handler instead of a dedicated builder.
- Failing to set `hovertemplate` or required axis titles.
- Re-running aggregation logic in the handler instead of the service layer.