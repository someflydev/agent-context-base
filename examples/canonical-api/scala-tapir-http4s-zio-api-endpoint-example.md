# Scala Tapir http4s ZIO API Endpoint Example

The endpoint description is declared as a value (`listReportsEndpoint`) separate from
the logic. `Http4sServerInterpreter[Task]().toRoutes(...)` converts it to `HttpRoutes[Task]`.
This separation means the endpoint is independently testable and can generate OpenAPI
specs without running the server.

**Route registration shape:** Tapir endpoint values (`endpoint.get.in(...).out(...)`) are
the contract; the http4s interpreter is the transport adapter. The endpoint description
is the canonical reference — change it first when modifying the API shape.

**Request parsing:** `path[String]("tenantId")` and `query[Option[Int]]("limit")` — typed
at the endpoint description level. The interpreter deserializes path and query params
before the handler sees them. No manual extraction required.

**Service/transport separation:** The logic in this example is inline in `serverLogicSuccess`
via `ZIO.succeed(ReportEnvelope(...))`. There is no service layer. When deriving, extract
a `ReportService` as a ZIO layer and inject it via the ZIO environment.

**Error handling:** `serverLogicSuccess` asserts no error path — the handler is expected to
always succeed. A DB failure inside `serverLogicSuccess` will propagate as an unhandled
ZIO defect, not a 500 response. Use `serverLogic` with `ZIO[R, ErrorType, Output]` and
map errors to Tapir error outputs for real endpoints. Do not use `serverLogicSuccess` on
any DB-backed route.

**Response shape:** `jsonBody[ReportEnvelope]` on the endpoint output. `JsonCodec[ReportEnvelope]`
is derived via `DeriveJsonCodec.gen` (ZIO JSON). Adding a field to the case class adds it
to the response automatically; removing one will break deserialization for clients that
expect it. No manual JSON wiring.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/scala-tapir-http4s-zio-api-endpoint-example.scala`
- `examples/canonical-api/scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
