# Kotlin http4k Exposed API Endpoint Example

`"/api/reports/{tenantId}" bind GET to { request -> ... }` produces a `RoutingHttpHandler`
value. There is no handler class or `Register()` method. Routes are assembled by composing
these values, typically inside a `routes(...)` block at the app entry point.

**Route registration shape:** http4k's functional routing idiom — routes are values, not
annotations or method registrations. The handler is an inline lambda. For a derived repo
with many routes, extract each lambda to a named function and reference it in the binding.

**Request parsing:** `request.path("tenantId")` returns `String?`; the `?: error(...)`
call throws `IllegalStateException` if absent (http4k converts it to a 500). Path params
are always strings — no automatic coercion. No query param extraction is shown.

**Service/transport separation:** The Exposed `transaction { }` block runs inline in the
route handler. There is no service or repository layer. This is a deliberate example
simplification. For a derived repo, extract the query into a repository function so the
handler can be tested without a DB connection.

**Error handling:** The `.singleOrNull() ?: ReportEnvelope(...)` fallback returns 200 with
stub data when no row is found, rather than 404. This is a simplification — a real
endpoint should return 404 when the tenant has no reports. Replace the fallback with
`return Response(Status.NOT_FOUND)` when deriving.

**Response shape:** `reportLens(payload, Response(Status.OK))` — `Body.auto<ReportEnvelope>().toLens()`
serializes `ReportEnvelope` to JSON via Jackson. The lens is a module-level `val`, reused
across calls. Adding a field to `ReportEnvelope` is automatically reflected in the
response; no lens changes needed.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/kotlin-http4k-exposed.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/kotlin-http4k-exposed-api-endpoint-example.kt`
- `examples/canonical-api/kotlin-http4k-exposed-example/src/main/kotlin/example/Main.kt`
