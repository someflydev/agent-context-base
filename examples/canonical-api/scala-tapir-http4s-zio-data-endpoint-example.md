# Scala Tapir http4s ZIO Data Endpoint Example

This example shows the preferred Scala data-endpoint shape for chart consumers:

- keep the dataset contract typed with Tapir and ZIO codecs
- return a stable JSON payload for Plotly-style consumers
- make the metric name explicit in both the route and the response payload

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/scala-tapir-http4s-zio-data-endpoint-example.scala`
- `examples/canonical-api/scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
