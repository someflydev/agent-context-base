# OCaml Dream Caqti TyXML API Endpoint Example

`reports_handler` receives the Caqti DB module as a partially applied argument and is
registered with `Dream.get "/api/reports/:tenant_id"`. The Caqti query is defined as a
module-level typed value, not inline.

**Route registration shape:** `Dream.get "/api/reports/:tenant_id" (reports_handler db)` —
plain Dream route value. `routes db` returns a list of such values for `Dream.run`. The
handler is a curried function; the `db` module is captured at startup.

**Request parsing:** `Dream.param request "tenant_id"` extracts the path segment as a
string. Limit uses `Option.bind (Dream.query request "limit") int_of_string_opt |> Option.value ~default:5`.
`int_of_string_opt` returns `None` on non-integer input — safe fallback. No upper clamp shown.

**Service/transport separation:** `select_reports` is a module-level Caqti typed request
(`Caqti_type.(t2 string int) ->* Caqti_type.(t3 string int string)`). The handler calls
`Db.collect_list select_reports (tenant_id, limit)`. There is no intermediate service
layer, but the query boundary is explicit via the Caqti type annotation. Extract query
functions to a separate module when deriving.

**Error handling:** `>>= Caqti_lwt.or_fail` — if the DB query fails, `or_fail` raises an
exception instead of returning an HTTP 500. The example has no `try/catch` or error
HTTP response path. Replace with `Lwt_result.bind` and a custom 502 response function
when deriving. Do not ship `or_fail` in production route handlers.

**Response shape:** `Dream.json (Yojson.Safe.to_string ...)` — a JSON string assembled
from a hand-built `` `Assoc `` tree. Every field is written explicitly as a Yojson
constructor. Verbose compared to derive macros, but every output field is visible at
the call site. Schema changes require editing the Yojson tree directly.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ocaml-dream-caqti-tyxml.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ocaml-dream-caqti-tyxml-api-endpoint-example.ml`
- `examples/canonical-api/ocaml-dream-caqti-tyxml-example/bin/main.ml`
