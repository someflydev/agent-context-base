# Dart: Dart Frog

Use this pack for Dart backend services that want Dart Frog route handlers, explicit JSON payload shaping, and small HTML fragment endpoints for HTMX-style updates.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `pubspec.yaml`
- `routes/`
- `lib/`
- `test/`
- `Dockerfile`
- `analysis_options.yaml`

## Common Change Surfaces

- Dart Frog route handlers and path-parameter extraction
- JSON envelope helpers for API and chart-data endpoints
- HTML fragment render helpers with stable HTMX markers
- runtime boot wiring and port configuration
- Dockerfiles used for smoke verification when host Dart tooling is absent

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API route with an explicit payload contract
- one HTML fragment response check with stable `id`, `class`, and `hx-swap-oob` markers
- one chart-data JSON payload check for interactive dashboard consumers

## Common Assistant Mistakes

- inferring path parameters implicitly instead of making route-to-handler flow obvious
- returning large inline maps or strings without naming the payload or fragment contract
- assuming host Dart or Dart Frog tooling exists when Docker-backed verification is the default path
