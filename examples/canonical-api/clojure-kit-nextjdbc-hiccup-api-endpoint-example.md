# Clojure Kit next.jdbc Hiccup API Endpoint Example

This example shows the preferred Clojure service shape for a Kit-flavored JSON endpoint:

- keep the route surface explicit in the Reitit route tree
- query storage through `next.jdbc` instead of embedding raw result maps in transport code
- encode the response boundary deliberately for assistant-visible API contracts

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-api-endpoint-example.clj`
- `examples/canonical-api/clojure-kit-nextjdbc-hiccup-example/src/clojure_kit_nextjdbc_hiccup_example/routes.clj`
