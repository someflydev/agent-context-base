# OCaml: Dream + Caqti + TyXML

Use this pack for OCaml backend services that want Dream for HTTP routing, Caqti for explicit database access, and TyXML for typed HTML fragment generation.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `dune-project`
- `*.opam`
- `bin/main.ml`
- `lib/db.ml`
- `lib/html.ml`
- `test/`

## Common Change Surfaces

- Dream router composition, middleware, and request decoding
- Caqti request definitions and connection lifecycle wiring
- TyXML fragment builders for HTMX-style partial updates
- JSON encoding for API and dataset responses
- Dockerfiles used for smoke verification when host OCaml tooling is absent

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API route that exercises a Caqti query path
- one TyXML fragment surface check with stable markers such as `hx-swap-oob`
- one chart-data payload check for interactive dashboard consumers

## Common Assistant Mistakes

- hiding the Dream route tree behind framework-agnostic helpers
- interpolating SQL strings inline instead of using named `Caqti_request` values
- emitting handwritten HTML strings when TyXML should define the fragment contract
