# Scala Tapir http4s ZIO HTML Fragment Example

This example shows the Scala stack posture for HTMX-style fragment responses:

- let http4s own the fragment transport surface
- keep the fragment renderer explicit and small
- return stable HTML markers such as `id`, `class`, and `hx-swap-oob`

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/scala-tapir-http4s-zio-html-fragment-example.scala`
- `examples/canonical-api/scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
