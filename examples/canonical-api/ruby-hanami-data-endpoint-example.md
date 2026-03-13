# Ruby Hanami Data Endpoint Example

This example shows the preferred Ruby plus Hanami chart-data shape:

- keep the route surface explicit in the Hanami router
- shape chart payloads through a small Sequel-backed repository helper
- return structured JSON that dashboard and Plotly-style clients can consume directly

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ruby-hanami.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ruby-hanami-data-endpoint-example.rb`
- `examples/canonical-api/ruby-hanami-example/app/actions/charts/show.rb`
- `examples/canonical-api/ruby-hanami-example/lib/ruby_hanami_example/persistence.rb`
