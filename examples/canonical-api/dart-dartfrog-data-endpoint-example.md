# Dart Dart Frog Data Endpoint Example

`chartPayload(String metric)` assembles the chart structure as a `Map<String, Object>`
with nested `List<Map<String, Object>>` for series and points. `Response.json` serializes
it automatically.

**Chart payload contract:** `{'metric': metric, 'series': [{'name': metric, 'points': [{'x': '...', 'y': N}]}]}` —
a plain Dart `Map` hierarchy matching the `{metric, series: [{name, points: [{x, y}]}]}`
chart contract. No typed class; shape is by convention.

**Typed response encoding:** `Response.json(body: chartPayload(metric))` — Dart Frog
calls `dart:convert`'s `jsonEncode` on the `Map`. `x` values are `String`, `y` values
are `int` — both JSON-serializable. If a non-serializable type (e.g., `DateTime`) is
added to the map, serialization will throw at runtime. Prefer typed model classes with
`toJson()` when the schema grows.

**Storage query integration:** The DB query is stubbed. `chartPayload` returns hardcoded
points. No database access or repository layer is shown. Replace the hardcoded point
list with a repository call when deriving.

**Metric parameter safety:** `metric` comes from `pathSegments.last` and flows only into
the response JSON — not into a SQL query. Safe in the stub. When adding a real query,
use parameterized queries and do not interpolate `metric` into raw SQL.

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/dart-dartfrog.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/dart-dartfrog-data-endpoint-example.dart`
- `examples/canonical-api/dart-dartfrog-example/routes/index.dart`
