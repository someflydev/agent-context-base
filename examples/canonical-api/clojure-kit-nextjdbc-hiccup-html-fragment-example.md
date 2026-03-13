# Clojure Kit next.jdbc Hiccup HTML Fragment Example

This example shows the preferred Clojure fragment surface for HTMX-style partial updates:

- keep the route shape explicit and narrow
- render the fragment through Hiccup instead of handwritten HTML assembly
- preserve stable markers such as fragment ids and `hx-swap-oob`

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-html-fragment-example.clj`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-example/src/clojure_kit_nextjdbc_hiccup_example/html.clj`
