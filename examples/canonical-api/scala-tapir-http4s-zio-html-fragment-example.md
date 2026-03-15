# Scala Tapir http4s ZIO HTML Fragment Example

The fragment route is handled directly with `Http4sDsl` pattern matching rather than
through a Tapir endpoint description — Tapir is not used here because HTML fragment
routes do not need typed API contracts or OpenAPI exposure.

**HTMX fragment contract:** `id="report-card-$tenantId"` and `hx-swap-oob="true"` are in
the interpolated string. The `id` is tenant-scoped, so each tenant's card is a distinct
swap target on the page. The surrounding page must contain an element with the matching
`id` for HTMX to apply the out-of-band swap.

**Content-type discipline:** `.withContentType(Content-Type(MediaType.text.html))` is
applied explicitly on the `Ok(...)` response via the http4s API. The content-type is not
inherited from a view layer. Do not omit it on fragment routes; HTMX and browsers may
misinterpret a response without an explicit `text/html` header.

**Server-side rendering approach:** Scala string interpolation — `s"""...""".stripMargin.trim`.
No HTML library. The HTML is a multiline string with `$tenantId` and `$totalEvents`
interpolated directly.

**Escaping and XSS posture:** `$totalEvents` is an `Int` — safe. `$tenantId` comes from
the URL path and is interpolated raw into the HTML string. If `tenantId` can contain
`<`, `>`, or `"`, this is an XSS risk. Use `StringEscapeUtils.escapeHtml4(tenantId)` or
route through ScalaTags when deriving if `tenantId` is not constrained by the auth layer.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/scala-tapir-http4s-zio-html-fragment-example.scala`
- `examples/canonical-api/scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
