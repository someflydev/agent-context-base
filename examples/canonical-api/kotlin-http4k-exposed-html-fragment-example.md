# Kotlin http4k Exposed HTML Fragment Example

This example shows the Kotlin stack posture for HTMX-style fragment responses:

- let `http4k` own the fragment transport surface
- keep the fragment renderer explicit and small
- return stable HTML markers such as `id`, `class`, and `hx-swap-oob`

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/kotlin-http4k-exposed.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/kotlin-http4k-exposed-html-fragment-example.kt`
- `examples/canonical-api/kotlin-http4k-exposed-example/src/main/kotlin/example/Main.kt`
