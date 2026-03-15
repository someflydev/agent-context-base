# Dart Dart Frog API Endpoint Example

Dart Frog uses file-system routing — `onRequest` is the handler for the path determined
by where this file sits under `routes/`. There is no explicit router configuration in
the handler. The function signature `Response onRequest(RequestContext context)` is the
Dart Frog handler contract.

**Route registration shape:** File-per-route. No router builder or `Register()` call.
The route path is the file path relative to `routes/`. Dynamic segments use bracket
syntax in the filename (e.g., `routes/[tenantId].dart`).

**Request parsing:** `context.request.uri.pathSegments.last` extracts the last path
segment as the tenant ID. This is a positional extraction, not a named param — it
depends on the file's depth in the route tree. For named params, use a dynamic route
file and `context.request.uri.pathSegments` with the correct index.
`context.request.uri.queryParameters['window'] ?? '24h'` extracts a query param with
a default — safe; returns `null` if absent, which the `??` catches.

**Service/transport separation:** `reportPayload(...)` is a plain helper function
returning a `Map<String, Object>`. There is no service class or DB access. All data is
stubbed — replace with a repository call when deriving.

**Error handling:** Not shown. `Response.json(body: ...)` always returns 200. Add
`if (tenantId.isEmpty) return Response(statusCode: 404)` and similar guards when deriving.

**Response shape:** `Response.json(body: reportPayload(...))` — Dart Frog serializes the
`Map<String, Object>` to JSON via `dart:convert`. All map values must be JSON-serializable.
No typed struct serialization; schema is enforced by convention only.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/dart-dartfrog.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/dart-dartfrog-api-endpoint-example.dart`
- `examples/canonical-api/dart-dartfrog-example/routes/index.dart`
