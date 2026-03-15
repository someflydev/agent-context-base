# Clojure Kit next.jdbc Hiccup API Endpoint Example

The route is a Reitit data structure: `["/api/reports/:tenant-id" {:get handler-fn}]`.
`report-endpoint` takes a `datasource` and returns the vector — this is how Kit services
inject the DB connection at component startup rather than via global state.

**Route registration shape:** Reitit route format — a vector of `[path method-map]`. The
handler is a plain function, not a class. Related routes can be grouped by nesting vectors.
No annotations; no reflection.

**Request parsing:** `{{tenant-id :tenant-id} :path-params}` destructures the Reitit
request map. Path params are keyword keys matching the `:tenant-id` segment. No limit
extraction is shown — add it via `(get-in request [:query-params :limit])` when deriving.

**Service/transport separation:** `jdbc/execute-one!` runs inline in the handler. There is
no service or repository namespace in the example. In Kit, inline queries are acceptable
for small routes; larger services should extract a repository namespace (e.g.,
`myapp.db.reports`) to keep handlers testable without a live DB.

**Error handling:** Not shown. If `execute-one!` returns `nil` (no matching row), the
response body includes `nil` values for all report keys. Add a `nil?` guard and return
`{:status 404 :body "not found"}` when deriving.

**Response shape:** Plain Ring response map with `clojure.data.json/write-str`. There is
no schema type enforcing the shape — any Clojure map passed to `write-str` is encoded
as-is. Consider `malli` or `spec` validation at the response boundary when deriving to
catch field drift early.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-api-endpoint-example.clj`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-example/src/clojure_kit_nextjdbc_hiccup_example/routes.clj`
