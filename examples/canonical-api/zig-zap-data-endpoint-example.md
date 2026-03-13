# Zig Zap Data Endpoint Example

This example shows the preferred Zig data-endpoint shape for chart consumers:

- keep dataset assembly in one helper
- return a stable JSON payload for Plotly-style clients
- make the series or metric identifier obvious in the route

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/zig-zap-jetzig.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/zig-zap-data-endpoint-example.zig`
- `examples/canonical-api/zig-zap-jetzig-example/main.zig`
