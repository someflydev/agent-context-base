# Kotlin: http4k + Exposed

Use this pack for Kotlin backend services that want explicit `http4k` route composition, Exposed-backed query helpers, and small HTML fragment or chart-data endpoints.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `build.gradle.kts`
- `settings.gradle.kts`
- `src/main/kotlin/`
- `src/test/kotlin/`
- `src/main/resources/`

## Common Change Surfaces

- `http4k` route composition and response lenses
- Exposed table definitions, transactions, and seed helpers
- JSON payload types used by API or chart endpoints
- HTML fragment render helpers for HTMX-style updates
- Dockerfiles used for smoke verification when host Gradle tooling is absent

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API route that exercises an Exposed query path
- one HTML fragment response check with stable `id`, `class`, and `hx-swap-oob` markers
- one chart-data JSON payload check for interactive dashboard consumers

## Common Assistant Mistakes

- hiding the real `http4k` route surface behind generic wrapper abstractions
- opening Exposed transactions inline in every handler instead of small named query helpers
- returning ad hoc maps or stringly payloads where typed response objects should define the contract
