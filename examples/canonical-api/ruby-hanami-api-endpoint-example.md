# Ruby Hanami API Endpoint Example

This example shows the preferred Ruby plus Hanami JSON endpoint shape:

- keep route registration explicit in the Hanami router
- let a small action class own the transport contract
- query persistence through a named Sequel helper instead of shaping records inline

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ruby-hanami.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ruby-hanami-api-endpoint-example.rb`
- `examples/canonical-api/ruby-hanami-example/app/actions/reports/show.rb`
- `examples/canonical-api/ruby-hanami-example/lib/ruby_hanami_example/persistence.rb`
