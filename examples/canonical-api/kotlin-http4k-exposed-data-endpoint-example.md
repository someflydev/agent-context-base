# Kotlin http4k Exposed Data Endpoint Example

This example shows the preferred Kotlin data-endpoint shape for chart consumers:

- keep the dataset contract typed with Kotlin payload classes and `http4k` lenses
- query ordered points through Exposed instead of shaping them in transport code
- return a stable JSON payload for Plotly-style consumers

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/kotlin-http4k-exposed.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/kotlin-http4k-exposed-data-endpoint-example.kt`
- `examples/canonical-api/kotlin-http4k-exposed-example/src/main/kotlin/example/Main.kt`
