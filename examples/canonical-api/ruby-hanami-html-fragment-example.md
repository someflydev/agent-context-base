# Ruby Hanami HTML Fragment Example

This example shows the preferred Ruby plus Hanami fragment-response shape:

- keep the endpoint as a small action class
- render the fragment through `Hanami::View` instead of hand-building HTML strings
- return a stable HTMX-friendly partial with explicit swap markers

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ruby-hanami.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ruby-hanami-html-fragment-example.rb`
- `examples/canonical-api/ruby-hanami-example/app/actions/report_cards/show.rb`
- `examples/canonical-api/ruby-hanami-example/app/views/report_cards/show.rb`
- the runtime bundle's report-card ERB fragment template
