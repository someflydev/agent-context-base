# Scala Tapir http4s ZIO Data Endpoint Example

`chartEndpoint` is a Tapir endpoint value separate from `buildPayload` and the route
logic — the same contract/implementation split used in the api-endpoint example. The
endpoint description is the authoritative schema definition.

**Chart payload contract:** `ChartPayload(metric: String, series: List[MetricSeries])`
where `MetricSeries(name, points: List[SeriesPoint(x: String, y: Int)])`. Matches the
`{metric, series: [{name, points: [{x, y}]}]}` chart contract. Enforced by case classes,
not assembled manually.

**Typed response encoding:** `JsonCodec[ChartPayload]`, `MetricSeries`, and `SeriesPoint`
are each derived via `DeriveJsonCodec.gen` (ZIO JSON). The endpoint declares `jsonBody[ChartPayload]`;
the interpreter handles serialization. Adding a field requires updating the case class;
removing one will break clients expecting it. No manual JSON wiring.

**Storage query integration:** The DB query is stubbed. `buildPayload(metric)` returns
hardcoded points (`2026-03-01`, `2026-03-02`, `2026-03-03`). Replace `buildPayload` with
a ZIO effect that queries a real data source when deriving.

**Metric parameter safety:** `metric` comes from Tapir's typed `path[String]("metric")`
and flows into `buildPayload` and then into the `ChartPayload` response. In the stub it
is only echoed — not used in SQL. When replacing with a real query, validate or allowlist
`metric` values before passing them to a database.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/scala-tapir-http4s-zio-data-endpoint-example.scala`
- `examples/canonical-api/scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
