# Clojure: Kit + next.jdbc + Hiccup

Use this pack for Clojure backend services that want Kit-style system wiring, `next.jdbc` for database access, and Hiccup for explicit HTML fragment contracts.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `deps.edn`
- `src/<app>/core.clj`
- `src/<app>/routes.clj`
- `src/<app>/db.clj`
- `src/<app>/html.clj`
- `resources/system.edn`
- `test/`

## Common Change Surfaces

- Kit route modules and Reitit handler maps
- Integrant system wiring and lifecycle boundaries
- `next.jdbc` datasource, query, and result-shaping helpers
- Hiccup fragment rendering for HTMX-style partial responses
- Dockerfiles used for smoke verification when host Clojure tooling is absent

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API route that exercises a `next.jdbc` query path
- one HTML fragment surface check when Hiccup fragments are part of the response contract
- one chart-data payload check when the service feeds interactive dashboards

## Common Assistant Mistakes

- flattening Kit-style system wiring into one large `-main` namespace
- pushing SQL shaping directly into route maps instead of named `next.jdbc` helpers
- returning hand-built HTML strings when Hiccup should define the fragment contract
