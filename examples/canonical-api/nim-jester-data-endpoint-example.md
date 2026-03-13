# Nim Jester Data Endpoint Example

This example shows the preferred Nim data-endpoint shape for chart consumers:

- keep dataset assembly in one helper
- return a stable JSON payload for Plotly-style clients
- keep the metric or series name explicit in the route

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/nim-jester-happyx.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/nim-jester-data-endpoint-example.nim`
- `examples/canonical-api/nim-jester-happyx-example/main.nim`
