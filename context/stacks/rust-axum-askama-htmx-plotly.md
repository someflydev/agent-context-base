# Rust: Axum + Askama + HTMX + Tailwind + Plotly

## Typical Repo Surface
- `src/main.rs` — Entrypoint
- `src/handlers/` — Axum route handlers
- `src/domain/analytics/` — Aggregation logic
- `src/charts/` — Plotly figure builders
- `templates/` — Askama template files
- `tests/` — Integration and unit tests

## Key Libraries
- `axum` — async HTTP framework with typed extractors
- `askama` — compile-time typed Jinja-like templates (good for fragment responses)
- `plotly` (`plotly.rs` crate) — typed figure and trace types; serde-compatible
- `serde`, `serde_json` — figure serialization and request deserialization
- `htmx` — partial page updates (CDN)
- `tailwindcss` — utility-first styling (CDN or compiled)
- `tokio` — async runtime
- `tower`, `tower-http` — middleware layer (static files, tracing)
- `axum-test` or `reqwest` — integration testing

## Figure Builder Pattern
```rust
use plotly::{Plot, Scatter};

pub fn build_daily_trend(data: &[DailyCount]) -> Plot {
    let mut plot = Plot::new();
    let trace = Scatter::new(dates, values).name("Trend");
    plot.add_trace(trace);
    // Add layout logic...
    plot
}

// Axum handler:
// Json(serde_json::to_value(&plot).unwrap()) 
// Or returning the inline HTML depending on setup.
```

## Askama Fragment Pattern
```rust
#[derive(Template)]
#[template(path = "partials/chart_panel.html")]
pub struct ChartPanelTemplate {
    pub title: String,
}

// Axum handler using askama_axum integration
pub async fn dashboard_handler(headers: HeaderMap) -> impl IntoResponse {
    if headers.contains_key("hx-request") {
        return ChartPanelTemplate { title: "Trend".into() }.into_response();
    }
    // Return full page...
}
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
- **Unit Tests:** Verify `plotly::Plot` returned from builder functions contains expected traces and layout before serialization.
- **Integration Tests:** Assert chart data shape using `axum-test` or `reqwest`. Ensure Askama fragment routes return 200 OK and valid HTML.
- **E2E Tests:** Ensure filters align with chart state.

## Common Assistant Mistakes
- Building figure logic inside Axum handlers.
- Serializing `Vec<Row>` instead of aggregated trace data.
- Not using serde-compatible Plotly types.
- Forgetting that Askama templates are compiled at build time.