# Nim Jester Data Endpoint Example

`buildSeriesPayload` is a `proc` that takes `metric: string` and returns a `JsonNode`
built with `%*{}`. The Jester route calls it with `@"metric"` (the path param) and
passes the result directly to `resp`.

**Chart payload contract:** `%*{"metric": metric, "series": [{"name": metric, "points": [{...}]}]}` —
a `JsonNode` literal matching the `{metric, series: [{name, points: [{x, y}]}]}` chart
contract. The structure is correct by the literal, not enforced by a type.

**Typed response encoding:** `%*{}` is Nim's JSON literal macro from `std/json`. It
constructs a `JsonNode` at runtime. Jester's `resp` with a `JsonNode` emits the body
with `application/json`. There are no codecs to derive — the JSON shape mirrors the Nim
literal. Adding a field means editing the `%*{}` literal directly; there is no compile-time
check on the resulting shape.

**Storage query integration:** The DB query is stubbed. `buildSeriesPayload` returns
hardcoded points (`2026-03-01`, `2026-03-02`, `2026-03-03`). No Nim ORM or SQL library
is used. Replace the hardcoded points with a real database query when deriving.

**Metric parameter safety:** `@"metric"` is Jester's path param accessor — a `string`.
It flows into `buildSeriesPayload` where it is used only as a JSON value, not in a SQL
query. Safe in the stub. When adding a real query, use parameterized SQL and do not
interpolate `metric` into a raw query string.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/nim-jester-happyx.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/nim-jester-data-endpoint-example.nim`
- `examples/canonical-api/nim-jester-happyx-example/main.nim`
