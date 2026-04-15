# Go: Echo + templ + HTMX + Tailwind + Plotly

## Typical Repo Surface
- `cmd/server/main.go` — Entrypoint
- `internal/api/` — Echo handlers and routing
- `internal/analytics/` — Aggregation and query logic
- `internal/charts/` — Plotly figure builders
- `internal/templates/` — `templ` components (pages and partials)
- `internal/models/` — Domain structures

## Key Libraries
- `echo` — lightweight HTTP router with middleware support
- `templ` (a-h/templ) — typed, compiled Go templates; ideal for fragment responses
- `plotly` — figure construction via explicit Go struct types + `encoding/json`
- `htmx` — partial page updates (CDN)
- `tailwindcss` — utility-first styling (CDN or compiled)
- `encoding/json`, `net/http` — stdlib serialization and handler interfaces
- `testing`, `net/http/httptest` — route and fragment testing
- `playwright` (optional) — browser-level testing

## Figure Builder Pattern
```go
// Explicit struct types for Plotly instead of a 3rd party library
type PlotlyTrace struct { ... }
type PlotlyLayout struct { ... }
type PlotlyFigure struct {
    Data   []PlotlyTrace `json:"data"`
    Layout PlotlyLayout  `json:"layout"`
}

func BuildDailyTrend(data []analytics.DailyCount) PlotlyFigure {
    // Construct PlotlyFigure from domain structs
    return PlotlyFigure{ /* ... */ }
}

// Handler: c.JSON(http.StatusOK, figure)
```

## templ Fragment Pattern
```go
// Echo handler conditionally rendering fragment
func DashboardHandler(c echo.Context) error {
    if c.Request().Header.Get("HX-Request") == "true" {
        return templates.ChartPanel(data).Render(c.Request().Context(), c.Response().Writer)
    }
    return templates.DashboardPage(data).Render(c.Request().Context(), c.Response().Writer)
}
```

## Tailwind + HTMX Filter Pattern
```go
templ FilterForm() {
    <form hx-get="/api/partials/chart-panel" hx-target="#chart-panel" hx-swap="outerHTML">
        <select name="status" class="bg-white border border-gray-300 text-sm rounded-lg p-2.5">
            <option value="active">Active</option>
        </select>
    </form>
}
```

## Testing Expectations
- **Unit Tests:** Verify `PlotlyFigure` structs have correct trace setups and layout properties before JSON encoding.
- **Integration Tests:** Use `httptest.NewRecorder` with `echo` context to verify chart JSON and HTML fragment responses.
- **E2E Tests:** Ensure HTMX swaps work end-to-end via Playwright (if applicable).

## Common Assistant Mistakes
- Building figure logic inside Echo handlers.
- Treating `templ` as raw `html/template` and losing type safety.
- JSON-encoding entire row result sets instead of aggregated traces.
- Not setting typed `PlotlyFigure` struct fields explicitly, resulting in malformed JSON for Plotly.js.