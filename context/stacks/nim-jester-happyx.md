# Nim: Jester + HappyX

Use this pack for Nim backend services that want small Jester routes, Docker-first verification, and HappyX when reactive HTML fragments are part of the response contract.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `*.nimble`
- `src/main.nim`
- `src/http/`
- `src/fragments/`
- `src/services/`
- `tests/smoke/`
- `tests/integration/`

## Common Change Surfaces

- Jester route declarations and response helpers
- HappyX component or fragment definitions
- JSON encoding and chart-dataset shaping
- runtime boot wiring and port configuration
- Dockerfiles used for smoke verification

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API happy path
- one HTML fragment surface check when HTMX-style updates are part of the contract
- one chart-data payload check when the service feeds interactive dashboards

## Common Assistant Mistakes

- pushing domain logic directly into a large Jester route block
- treating HTML fragments as throwaway strings instead of an explicit contract surface
- assuming host Nim tooling exists when Docker-backed verification is the default path
