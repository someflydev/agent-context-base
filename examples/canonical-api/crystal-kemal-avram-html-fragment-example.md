# Crystal Kemal Avram HTML Fragment Example

This example shows the preferred Crystal shape for an HTMX-friendly fragment endpoint:

- keep Kemal responsible for routing and response headers
- use an Avram query object to fetch the fragment payload boundary
- return stable fragment markup instead of ad hoc string assembly

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/crystal-kemal-avram.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/crystal-kemal-avram-html-fragment-example.cr`
- `examples/canonical-api/crystal-kemal-avram-example/src/app.cr`
