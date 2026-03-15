# TypeScript Hono Handler Example

A `Hono` router instance with one `.get()` call exported as `reportsRouter`. No handler
class, no `Register()` method. Hono routers are composable module-level values; mounting
happens in the app entry point.

**Route registration shape:** `reportsRouter.get("/tenants/:tenantId/reports", async (context) => { ... })`.
The handler is an async inline function. Route ordering follows declaration order in the file.

**Request parsing:** `context.req.param("tenantId")` and `context.req.query("limit")`.
Limit is parsed with `Number.parseInt(..., 10)`, defaulting to 10 on a falsy value, and
clamped to 50 via `Math.min`. No schema validation — `tenantId` is passed directly into
the Drizzle query without sanitization.

**Service/transport separation:** There is no service layer. The Drizzle ORM query runs
inline in the handler. This is idiomatic for small Bun/Hono services. For a larger surface,
extract a repository function. Be explicit about this choice when deriving; inlining ORM
calls makes the handler harder to unit-test.

**Error handling:** Not shown. An unhandled Drizzle error will surface as an unhandled
promise rejection. Wrap the handler body in `try { ... } catch (e) { return context.json({ error: "..." }, 502) }`
when deriving.

**Response shape:** `context.html(<JSX>)` — this endpoint returns HTML, not JSON. The JSX
is compiled at build time by Bun's JSX transform; it is not evaluated at runtime. `context.html()`
sets `Content-Type: text/html` automatically. If you need a JSON endpoint, use `context.json(...)`
instead and replace the JSX with a typed response object.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/typescript-hono-bun-drizzle.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/typescript-hono-handler-example.ts`
