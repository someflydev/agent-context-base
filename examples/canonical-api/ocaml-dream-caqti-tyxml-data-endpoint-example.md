# OCaml Dream Caqti TyXML Data Endpoint Example

This example shows the preferred OCaml shape for chart-oriented JSON data endpoints:

- keep the metric route explicit in Dream
- fetch ordered data points through `Caqti_request`
- shape the payload for charting consumers before encoding it

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ocaml-dream-caqti-tyxml.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ocaml-dream-caqti-tyxml-data-endpoint-example.ml`
- `examples/canonical-api/ocaml-dream-caqti-tyxml-example/bin/main.ml`
