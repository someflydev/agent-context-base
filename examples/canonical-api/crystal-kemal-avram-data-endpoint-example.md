# Crystal Kemal Avram Data Endpoint Example

The same Avram model/query class separation used in the api-endpoint applies here.
`MetricPointQuery.new.for_metric(metric)` returns an Avram query that maps to
`SeriesPoint` structs. `ChartPayload.new(...).to_json` serializes the complete payload.

**Chart payload contract:** `ChartPayload(metric: String, series: Array(MetricSeries))`
where `MetricSeries(name: String, points: Array(SeriesPoint))` and `SeriesPoint(x: String, y: Int32)`.
All structs include `JSON::Serializable`. Matches the `{metric, series: [{name, points: [{x, y}]}]}`
chart contract. Enforced at compile time by the struct definitions.

**Typed response encoding:** `ChartPayload.new(...).to_json` — Crystal's `JSON::Serializable`
generates the codec at compile time via the `include` mixin. Field names match struct
property names by default. Use `@[JSON::Field(key: "...")]` to rename. Adding a field
adds it to the output automatically; no manual JSON wiring.

**Storage query integration:** `MetricPointQuery.new.for_metric(metric_name)` chains
`.metric(metric_name)` — Avram's column-equality helper, which generates a parameterized
SQL query. Safe from SQL injection. The `.map { ... }` block converts results to
`SeriesPoint` structs. The `if points.empty?` guard falls back to hardcoded stub points
— a deliberate example simplification. Replace with an empty series or 404 when deriving.

**Metric parameter safety:** Avram's DSL generates parameterized SQL — `metric` is not
interpolated into a raw query string. Safe from injection. `metric` is also echoed into
`ChartPayload.metric` and `MetricSeries.name`; normalize if your frontend treats the
metric name as a display or storage key.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/crystal-kemal-avram.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/crystal-kemal-avram-data-endpoint-example.cr`
- `examples/canonical-api/crystal-kemal-avram-example/src/app.cr`
