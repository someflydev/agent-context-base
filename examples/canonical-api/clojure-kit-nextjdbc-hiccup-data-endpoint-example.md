# Clojure Kit next.jdbc Hiccup Data Endpoint Example

`chart-endpoint` takes a `datasource` and returns a Reitit route vector with an inline
handler. The handler runs a parameterized SQL query and assembles the chart payload
as a Clojure map before encoding it with `json/write-str`.

**Chart payload contract:** `{:metric metric :series [{:name metric :points [{:x bucket_day :y total}]}]}` —
assembled as a plain Clojure map and serialized with `clojure.data.json/write-str`.
Keyword keys become string keys in the output. Matches the `{metric, series: [{name, points: [{x, y}]}]}`
chart contract by convention, not by type enforcement.

**Typed response encoding:** `clojure.data.json/write-str` encodes any Clojure-serializable
map. There are no codecs to derive or maintain. Flexibility makes schema drift easy to
introduce silently. Document the expected chart shape explicitly when deriving, or add
`malli` validation before encoding.

**Storage query integration:** `jdbc/execute!` runs a parameterized query:
`"select bucket_day, total from metric_points where metric = ?"`. The `?` placeholder
prevents SQL injection. Rows are mapped to `{:x bucket_day :y total}` via `mapv`.
The query is inline in the handler — extract it to a repository namespace for testability
when deriving.

**Metric parameter safety:** `metric` is used as the SQL `?` parameter — safe from
injection. It is also echoed into the response as `:metric` and `:name`. No sanitization
shown. Normalize (trim, lowercase) if your frontend treats the metric name as a key.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-data-endpoint-example.clj`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-example/src/clojure_kit_nextjdbc_hiccup_example/db.clj`
