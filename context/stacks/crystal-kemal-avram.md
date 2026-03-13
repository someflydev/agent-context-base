# Crystal: Kemal + Avram

Use this pack for Crystal backend services that want Kemal route handling, Avram-shaped data boundaries, and Docker-first verification for runnable examples.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `shard.yml`
- `src/**/*.cr`
- `src/http/`
- `src/queries/`
- `src/fragments/`
- `db/migrations/`
- `spec/`

## Common Change Surfaces

- Kemal route declarations and request param handling
- Avram model, query, and operation boundaries
- HTML fragment helpers for HTMX-style partial updates
- JSON dataset shaping for chart and dashboard consumers
- Dockerfiles used for reproducible smoke verification

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API happy path
- one HTML fragment surface check when partial updates are part of the contract
- one chart-data payload check when the service feeds interactive dashboards

## Common Assistant Mistakes

- pushing data-shaping logic directly into a large Kemal block instead of a small query or service boundary
- treating Avram as invisible plumbing instead of showing the query or model surface explicitly
- assuming Crystal toolchains exist on the host when Docker-backed verification is the default path
