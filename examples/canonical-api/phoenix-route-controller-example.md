# Phoenix Route Controller Example

Two files form this example: the controller (`phoenix-route-controller-example.ex`) and
the router scope (`phoenix-router-surface-example.ex`). Read both together.

**Route registration shape:** `get "/tenants/:tenant_id/reports", ReportController, :index`
inside `scope "/", ExampleWeb` with `pipe_through :browser`. The `:browser` pipeline adds
session fetching, CSRF protection, and layout wrapping. For a JSON API, use
`pipe_through :api` — that pipeline strips the HTML-specific plugs. Using `:browser`
here means this route produces an HTML response by convention.

**Request parsing:** `%{"tenant_id" => tenant_id} = params` destructures the merged
path/query params map. Limit is extracted via `Map.get(params, "limit", "20")` and
piped through `String.to_integer() |> min(100)`. Note: `String.to_integer/1` raises
`ArgumentError` on non-integer input — it does not return an error tuple. Use
`Integer.parse/1` and guard against `:error` when `limit` is user-supplied.

**Service/transport separation:** The controller calls `Reporting.list_recent_reports(tenant_id, limit: limit)`.
`Reporting` is a Phoenix context module — the canonical Phoenix pattern keeps controllers
free of business logic; all data access lives in context modules. The controller's only
jobs are parsing params and calling `render/3`. Do not move query logic into the controller
when deriving.

**Error handling:** Not shown. `Reporting.list_recent_reports/2` is not defined in these
files. If it raises or returns `{:error, reason}`, the controller will crash. Add a
`case` or `with` block and return 404 or 502 as appropriate when deriving.

**Response shape:** `render(conn, :index, tenant_id: tenant_id, summaries: summaries)` —
renders an HTML template via Phoenix's view/template layer. The `:browser` pipeline
wraps this in the root layout. To return JSON instead, use `json(conn, %{...})` and
route through `:api`.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/elixir-phoenix.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/phoenix-route-controller-example.ex`
- `examples/canonical-api/phoenix-router-surface-example.ex`
