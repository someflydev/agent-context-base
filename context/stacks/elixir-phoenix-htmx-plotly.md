# Elixir: Phoenix + HEEx + HTMX + Tailwind + Plotly

## When to Use HTMX over LiveView
HTMX + Phoenix controllers are appropriate when the application already uses HTMX as the interactivity layer (parity with other stacks in this arc), when the team wants to avoid Phoenix PubSub and WebSocket overhead for simple filter-and-chart interactions, or when building reference examples that compare server-rendered HTMX across multiple language stacks. LiveView is not wrong — it is just a different pattern with different tradeoffs.

## Typical Repo Surface
- `mix.exs`, `config/`
- `lib/<app>_web/router.ex`
- `lib/<app>_web/controllers/` (NOT LiveView controllers)
- `lib/<app>_web/templates/` (HEEx templates for pages and partials)
- `lib/<app>/analytics/` (aggregation context modules)
- `lib/<app>/charts/` (figure builder modules)
- `test/`

## Key Libraries
- `phoenix` — HTTP framework with controller + HEEx template pipeline
- `plotly` (JSON construction via Elixir maps/structs + `Jason`)
- `jason` — JSON encoding/decoding
- `htmx` — partial page updates (CDN)
- `tailwindcss` — utility-first styling (Phoenix already includes this)
- `ecto`, `postgrex` — data access (or ETS / in-memory for examples)
- `ExUnit` — testing
- `playwright` (optional) — browser-level testing

## Figure Builder Pattern
```elixir
defmodule MyApp.Charts.DailyTrend do
  def build_figure(data) do
    %{
      data: [%{x: data.dates, y: data.values, type: "scatter", name: "Trend"}],
      layout: %{title: "Daily Trend"}
    }
  end
end

# Controller:
# conn |> json(MyApp.Charts.DailyTrend.build_figure(data))
```

## HEEx Fragment Pattern
```elixir
def dashboard(conn, params) do
  if get_req_header(conn, "hx-request") != [] do
    render(conn, "chart_panel.html", data: data)
  else
    render(conn, "dashboard.html", data: data)
  end
end
```

## Tailwind + HTMX Filter Pattern
```html
<form hx-get="/api/partials/chart-panel" hx-target="#chart-panel" hx-swap="outerHTML">
  <select name="status" class="bg-white border border-gray-300 text-sm rounded-lg p-2.5">
    <option value="active">Active</option>
  </select>
</form>
```

## Testing Expectations
- **Unit Tests:** ExUnit tests for aggregation context and figure builder modules.
- **Integration Tests:** ExUnit smoke tests for controller routes (`conn()` + `get`/`post` helpers) against real PostgreSQL (or ETS) for filter alignment.

## Common Assistant Mistakes
- Reaching for LiveView when HTMX is the stated pattern.
- Encoding Plotly JSON manually in controller instead of figure builder.
- Not separating analytics context from charts module.
- Missing `jason` dependency.