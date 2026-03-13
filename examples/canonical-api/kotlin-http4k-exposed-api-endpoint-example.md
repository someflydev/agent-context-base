# Kotlin http4k Exposed API Endpoint Example

This example shows the preferred Kotlin service shape for a storage-backed JSON endpoint:

- keep the `http4k` route surface explicit
- query storage through Exposed helpers instead of embedding row-shaping logic in transport code
- encode the response contract with typed payloads and JSON lenses

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/kotlin-http4k-exposed.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/kotlin-http4k-exposed-api-endpoint-example.kt`
- `examples/canonical-api/kotlin-http4k-exposed-example/src/main/kotlin/example/Main.kt`
