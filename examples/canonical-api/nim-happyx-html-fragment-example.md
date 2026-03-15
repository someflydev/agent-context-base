# Nim HappyX HTML Fragment Example

Two mechanisms appear in this file: a HappyX `component ReportSummaryCard` and a plain
`proc renderReportSummaryCard`. The Jester route calls `renderReportSummaryCard` — the
string interpolation version. The HappyX component is a companion for client-side or
SSR-via-HappyX use; it is not wired to the Jester route.

**HTMX fragment contract:** `id="report-summary-card"` and `hx-swap-oob="true"` are in
`renderReportSummaryCard`'s `fmt"""..."""` string. The `id` is **not** tenant-scoped —
it is the static string `"report-summary-card"`. Multiple tenants share this swap target
on any page that uses this fragment. If multi-tenant pages need distinct targets, change
the `id` to `"report-summary-card-{tenantId}"` and update the surrounding page to match.

**Content-type discipline:** Jester's `resp` with a string argument defaults to `text/html`.
No explicit content-type header is set. This is implicit behavior; if Jester's default
changes or the argument type changes, the content-type may differ silently.

**Server-side rendering approach:** `fmt"""..."""` — Nim's `strformat` module string
interpolation. `{tenantId}` and `{totalEvents}` are interpolated at call time. No HTML
builder or escaping library is involved.

**Escaping and XSS posture:** `strformat` does not HTML-escape values. `{tenantId}`
comes from the URL path and is interpolated raw. `{totalEvents}` is an `int` — safe.
If `tenantId` can contain `<`, `>`, or `"`, apply HTML escaping before interpolation
when deriving.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/nim-jester-happyx.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/nim-happyx-html-fragment-example.nim`
- `examples/canonical-api/nim-jester-happyx-example/main.nim`
