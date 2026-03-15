# Rust Axum Route Example

Axum's extractor model is the defining feature of this example. The handler signature
declares `State`, `Path`, and `Query` as typed function parameters; Axum deserializes
each before the function body runs.

**Route registration shape:** `Router::new().route("/tenants/:tenant_id/reports", get(list_reports)).with_state(state)` —
functional, not a handler struct. `AppState` is `Clone` (required by Axum) and holds
an `Arc<ReportService>`. State is threaded through `State<AppState>` at the extractor level.

**Request parsing:** `#[derive(Deserialize)]` on `ListReportsQuery` — Axum deserializes
the query string automatically. Limit is clamped with `.unwrap_or(20).min(100)`. No manual
`strconv` or `parseInt`; the type system does the work.

**Service/transport separation:** `AppState.report_service` is an `Arc<ReportService>`,
injected at router construction. The handler calls `report_service.list_recent(...)`. The
`ReportService` in this example is a stub returning hardcoded data — replace the body
with a real query when deriving.

**Error handling:** `.expect("surface a real error type in the app")` is a deliberate
placeholder. It will panic on any service error. Replace with `?` and return
`Result<impl IntoResponse, AppError>` from the handler. A `From<anyhow::Error> for AppError`
impl is the standard Axum pattern for mapping service errors to HTTP responses.

**Response shape:** `Json(reports)` — Axum wraps `Vec<ReportSummary>` in a JSON body.
`ReportSummary` uses `#[derive(Serialize)]`. Field renames require `#[serde(rename = "...")]`.
Schema evolution is safe: adding derived fields requires no manual JSON wiring.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/rust-axum.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/rust-axum-route-example.rs`
- `examples/canonical-api/rust-axum-example/src/main.rs`
