# Nim Jester JSON Endpoint Example

The route is a `get "/api/health":` block inside the `routes:` macro. There is no handler
struct, no router builder, and no explicit return — `resp` is the Jester macro that sets
the response body and status.

**Route registration shape:** `routes:` / `get "/path":` — Jester's macro DSL. The route
body executes in a special Jester scope where `resp`, `request`, and `params` are bound.
Route bodies are effectively inline — no `Register()` indirection.

**Request parsing:** No path or query params are extracted in this example. The route is
a fixed path. To add path params, use Jester's `@"paramName"` syntax
(e.g., `get "/api/:name": resp @"name"`). No automatic type coercion.

**Service/transport separation:** Not shown. `HealthSnapshot` is constructed inline in
the route body. There is no service struct or delegated call. Nim Jester examples do not
demonstrate a service separation pattern — logic is co-located with the route.

**Error handling:** Not shown. A Nim exception inside a `routes:` block surfaces as a
500 response. Add explicit `try/except` and set `response.code = Http404` (or other
status) when deriving.

**Response shape:** `resp %*{"service": snapshot.service, "status": snapshot.status}` —
`%*{}` is Nim's JSON literal macro from `std/json`, constructing a `JsonNode` at runtime.
Jester's `resp` emits a `JsonNode` as the body with `application/json` content-type
automatically.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/nim-jester-happyx.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/nim-jester-json-endpoint-example.nim`
- `examples/canonical-api/nim-jester-happyx-example/main.nim`
