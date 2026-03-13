# Crystal Kemal Avram API Endpoint Example

This example shows the preferred Crystal service shape for a JSON API endpoint:

- keep the Kemal route small and explicit
- make the Avram query boundary visible at the handler edge
- return a stable JSON envelope for downstream clients

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/crystal-kemal-avram.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/crystal-kemal-avram-api-endpoint-example.cr`
- `examples/canonical-api/crystal-kemal-avram-example/src/app.cr`
