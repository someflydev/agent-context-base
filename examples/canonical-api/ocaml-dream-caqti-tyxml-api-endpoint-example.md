# OCaml Dream Caqti TyXML API Endpoint Example

This example shows the preferred OCaml service shape for a Dream-backed JSON endpoint:

- keep the Dream route surface explicit
- define the SQL boundary with `Caqti_request`
- shape the JSON response deliberately before returning it

Use it with:

- `context/workflows/add-api-endpoint.md`
- `context/stacks/ocaml-dream-caqti-tyxml.md`
- `context/doctrine/testing-philosophy.md`

Related files:

- `examples/canonical-api/ocaml-dream-caqti-tyxml-api-endpoint-example.ml`
- `examples/canonical-api/ocaml-dream-caqti-tyxml-example/bin/main.ml`
