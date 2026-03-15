# Crystal Kemal Avram HTML Fragment Example

`render_report_card` returns a Crystal heredoc string with `#{}` interpolation. The
Kemal route block calls it after setting `env.response.content_type` and passes the
result as the response body. No Avram query is shown in the example — the fragment
data comes from the Avram query result or a fallback via `.try(&.field) || default`.

**HTMX fragment contract:** `id="report-card-#{tenant_id}"` and `hx-swap-oob="true"` are
present in the heredoc. The `id` is tenant-scoped. The surrounding page must contain an
element with the matching `id` for the out-of-band swap to apply.

**Content-type discipline:** `env.response.content_type = "text/html; charset=utf-8"` is
set explicitly on the Kemal response object before the block returns. Kemal defaults to
`text/plain` for string responses; this must be set explicitly for HTML fragment routes.

**Server-side rendering approach:** Crystal heredoc string (`<<-HTML ... HTML`) with `#{}`
interpolation. No template engine or HTML builder. `render_report_card` is a standalone
function returning a `String`.

**Escaping and XSS posture:** Crystal `#{}` heredoc interpolation does not HTML-escape
values. `#{tenant_id}` and `#{status}` are inserted raw. `#{total_events}` is `Int32` —
safe. `tenant_id` comes from the URL path and `status` from the DB; if either can
contain `<`, `>`, or `"`, add `HTML.escape(value)` from Crystal's standard library
when deriving.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/crystal-kemal-avram.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/crystal-kemal-avram-html-fragment-example.cr`
- `examples/canonical-api/crystal-kemal-avram-example/src/app.cr`
