# Dart Dart Frog Data Endpoint Example

This example shows the preferred Dart Frog data-endpoint shape for chart consumers:

- keep dataset assembly in one helper
- return a stable JSON payload for Plotly-style clients
- make the metric name explicit in the route surface

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/dart-dartfrog.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/dart-dartfrog-data-endpoint-example.dart`
- `examples/canonical-api/dart-dartfrog-example/routes/index.dart`
