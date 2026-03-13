# Scala Tapir http4s ZIO API Endpoint Example

This example shows the preferred Scala service shape for a typed JSON endpoint:

- define the contract with Tapir first
- let the http4s interpreter expose the route surface
- keep ZIO logic small and explicit at the endpoint boundary

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/scala-tapir-http4s-zio-api-endpoint-example.scala`
- `examples/canonical-api/scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
