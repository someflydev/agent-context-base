# Clojure Kit next.jdbc Hiccup Data Endpoint Example

This example shows the preferred Clojure shape for chart-oriented JSON data endpoints:

- keep the metric route explicit in the transport layer
- fetch ordered data points with `next.jdbc`
- shape the payload for Plotly-style or dashboard consumers before encoding it

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-data-endpoint-example.clj`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-example/src/clojure_kit_nextjdbc_hiccup_example/db.clj`
