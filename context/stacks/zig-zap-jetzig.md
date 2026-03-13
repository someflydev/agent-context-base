# Zig: Zap + Jetzig

Use this pack for Zig backend services that want Zap for lean HTTP transport and Jetzig-style file-system views when HTML fragments are an explicit contract surface.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `build.zig`
- `build.zig.zon`
- `src/main.zig`
- `src/http/`
- `src/views/`
- `tests/smoke/`
- `tests/integration/`

## Common Change Surfaces

- Zap request dispatch and content-type handling
- Jetzig view files and `renderTemplate` boundaries
- chart dataset shaping for dashboard consumers
- Dockerfiles used for container-first verification
- `build.zig` dependency wiring for Zig packages

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API happy path
- one HTML fragment surface check when HTMX-style partial updates matter
- one chart-data payload check when the service feeds interactive dashboards

## Common Assistant Mistakes

- treating Zap as if it were a batteries-included MVC framework
- writing Jetzig fragments as throwaway strings instead of explicit template surfaces
- assuming host Zig tooling exists when Docker-backed verification is the default path
