# Crystal Kemal Avram API Endpoint Example

Avram separates model definition from query logic via two classes: `ReportSnapshot < BaseModel`
describes the table columns, and `ReportSnapshotQuery < ReportSnapshot::BaseQuery` provides
the query DSL. Models are never queried directly — always through a query class. This
is Avram's idiomatic pattern; preserve it when deriving.

**Route registration shape:** `get "/api/reports/:tenant_id" do |env| ... end` — Kemal's
block-based routing macro. Routes are registered at the top level in declaration order.
Kemal uses first-match routing for overlapping patterns.

**Request parsing:** `env.params.url["tenant_id"]` extracts the path param as a `String`.
Kemal does not coerce types — all params are strings and require manual conversion. No
limit param extraction is shown.

**Service/transport separation:** The Avram query and the `ReportEnvelope` construction
run inline in the Kemal block. There is no service layer. The query boundary is explicit
via `ReportSnapshotQuery.new.for_tenant(tenant_id).first?`, but there is no service
object between the handler and the query class.

**Error handling:** The `else` branch of the `if snapshot` conditional returns 200 with
stub data instead of 404. This is a deliberate example simplification. When deriving,
replace the else branch with `env.response.status_code = 404; next` followed by an
appropriate error body.

**Response shape:** `ReportEnvelope.new(...).to_json` — Crystal's `JSON::Serializable`
mixin generates the serializer at compile time. `include JSON::Serializable` on both
`ReportEnvelope` and `ReportSummary` structs. Adding a field to a struct adds it to the
JSON output automatically.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/crystal-kemal-avram.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/crystal-kemal-avram-api-endpoint-example.cr`
- `examples/canonical-api/crystal-kemal-avram-example/src/app.cr`
