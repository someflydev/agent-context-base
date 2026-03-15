# Kotlin http4k Exposed Data Endpoint Example

The same lens pattern used in the api-endpoint example applies here: `Body.auto<ChartPayload>().toLens()`
is a module-level `val` that serializes `ChartPayload` to JSON via Jackson. The route
lambda assembles the payload, then applies the lens to the response.

**Chart payload contract:** `ChartPayload(metric: String, series: List<MetricSeries>)`
where `MetricSeries(name: String, points: List<SeriesPoint>)` and `SeriesPoint(x: String, y: Int)`.
Matches the `{metric, series: [{name, points: [{x, y}]}]}` chart contract. Enforced by
data classes; no manual JSON assembly.

**Typed response encoding:** `chartLens(payload, Response(Status.OK))` — Jackson serializes
all fields by default. Adding a field to `ChartPayload` or `SeriesPoint` requires no lens
changes. Field renames need `@JsonProperty`. No schema evolution guard; breaking changes
are silent at the serialization boundary.

**Storage query integration:** `MetricPoints` Exposed `Table` is queried inline in the
`transaction { }` block. The query selects `bucket_day` and `total` ordered by `bucketDay ASC`.
`.ifEmpty { ... }` returns hardcoded stub points when the query is empty — a deliberate
simplification. Replace the stub with an empty series or a 404 response when deriving.

**Metric parameter safety:** `metric` flows into `MetricPoints.metric eq metric` via
Exposed's DSL. Exposed uses parameterized queries — SQL injection is not a risk. The
same `metric` value is echoed into `ChartPayload.metric` and `MetricSeries.name`;
normalize it (trim, lowercase) if your frontend depends on consistent casing.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/kotlin-http4k-exposed.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/kotlin-http4k-exposed-data-endpoint-example.kt`
- `examples/canonical-api/kotlin-http4k-exposed-example/src/main/kotlin/example/Main.kt`
