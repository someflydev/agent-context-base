# Kotlin http4k Exposed HTML Fragment Example

`renderReportCard` builds the fragment as a Kotlin multiline string with `trimIndent()`.
The route lambda sets the content-type header manually and returns the string as the
response body. No template engine or HTML builder is involved.

**HTMX fragment contract:** `id="report-card-$tenantId"` and `hx-swap-oob="true"` are
present in the heredoc. The `id` is tenant-scoped. The surrounding page must contain an
element with the matching `id` for the out-of-band swap to apply. If the page uses a
static `id="report-card"`, update the Kotlin-side `id` construction to match.

**Content-type discipline:** `.header("content-type", "text/html; charset=utf-8")` is set
explicitly on the http4k `Response` object. There is no view layer that sets it
implicitly. Omitting it will cause http4k to emit no content-type header, which may
lead HTMX to treat the response as `text/plain`.

**Server-side rendering approach:** Kotlin multiline string with `trimIndent()`. `$tenantId`
and `$totalEvents` are Kotlin string template interpolations. No escaping library is
involved.

**Escaping and XSS posture:** Kotlin string templates do not HTML-escape values. `$tenantId`
is interpolated raw into the markup. If `tenantId` comes from a user-controlled path
segment and is not validated by an auth layer, this is an XSS risk. Escape with
`StringEscapeUtils.escapeHtml4(tenantId)` (Apache Commons Text) or switch to a
templating library when deriving.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/kotlin-http4k-exposed.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/kotlin-http4k-exposed-html-fragment-example.kt`
- `examples/canonical-api/kotlin-http4k-exposed-example/src/main/kotlin/example/Main.kt`
