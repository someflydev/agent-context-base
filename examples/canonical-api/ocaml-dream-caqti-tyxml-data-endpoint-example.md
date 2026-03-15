# OCaml Dream Caqti TyXML Data Endpoint Example

`data_handler` follows the same partial-application pattern as the api-endpoint: the
Caqti DB module is injected at startup via currying. `select_points` is a module-level
typed Caqti request — separate from the handler body.

**Chart payload contract:** The response is a hand-built Yojson tree:
`` `Assoc [("metric", ...); ("series", `List [`Assoc [("name", ...); ("points", `List [...])]])] ``.
Matches the `{metric, series: [{name, points: [{x, y}]}]}` chart contract. The structure
is correct by inspection, not enforced by a type.

**Typed response encoding:** `Yojson.Safe.to_string` serializes the `` `Assoc `` tree.
Every field is written as a Yojson constructor (`"x", `String x`; `"y", `Int y``). No
derive macros. This is OCaml's value-layer JSON approach — verbose but transparent. Schema
changes require editing the Yojson tree directly at the call site.

**Storage query integration:** `select_points` is typed as `Caqti_type.string ->* Caqti_type.(t2 string int)` —
one input (metric), returns a list of `(string, int)` pairs representing `(bucket, value)`.
`Db.collect_list select_points metric` runs the query. The `?` SQL placeholder prevents
SQL injection. `>>= Caqti_lwt.or_fail` raises on DB error — same caveat as the api-endpoint:
a DB failure is an unhandled exception, not a 500. Replace with a proper error response
when deriving.

**Metric parameter safety:** `metric` is passed as the Caqti `?` parameter — safe from
injection. It is also echoed into the response as `"metric"` and `"name"` values. No
sanitization shown. Normalize if your frontend treats the metric name as a key.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ocaml-dream-caqti-tyxml.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ocaml-dream-caqti-tyxml-data-endpoint-example.ml`
- `examples/canonical-api/ocaml-dream-caqti-tyxml-example/bin/main.ml`
