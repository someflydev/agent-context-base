# Go Echo Handler Example

The handler is a struct (`ReportHandler`) holding a `*services.ReportService` pointer.
`Register(group *echo.Group)` binds the route at wire-up time — this is the preferred
Go-Echo idiom for grouping related routes without closures.

**Route registration shape:** `Register` attaches `ListRecent` to the group. The handler
receives the group once at startup, not at request time. Related routes live together
in one type, which makes the surface easy to scan.

**Request parsing:** `c.Param("tenantID")` returns a string; no automatic coercion.
Limit is parsed with `strconv.Atoi`; an error or non-positive result falls back to 10.
There is no upper clamp — add `min(limit, N)` when deriving to avoid unbounded DB queries.

**Service/transport separation:** `services.ReportService` is injected via the struct and
called as `handler.Reports.ListRecent(ctx, tenantID, limit)`. The handler does not touch
the database. This is a clean boundary; preserve it when deriving.

**Error handling:** A service error returns `echo.NewHTTPError(http.StatusBadGateway, ...)` —
502, not 500. This signals that an upstream dependency failed, not that the request was
malformed. A missing-tenant 404 is not shown; add it when the service returns nothing.

**Response shape:** This endpoint returns HTML, not JSON. The content-type is set via
`echo.MIMETextHTMLCharsetUTF8` before calling `views.ReportSummaryList(summaries).Render(...)`.
The view is a typed Templ component. Do not treat this as a JSON API endpoint; if you need
JSON output, return `c.JSON(...)` from a new handler instead.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/go-echo.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/go-echo-handler-example.go`
- `examples/canonical-api/go-echo-example/main.go`
