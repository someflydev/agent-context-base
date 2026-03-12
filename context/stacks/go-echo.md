# Go: Echo + templ

Use this pack for Go services that need a pragmatic HTTP stack and server-rendered HTML components via `templ`.

## Typical Repo Surface

- `go.mod`
- `cmd/server/main.go`
- `internal/http/`
- `internal/views/`
- `internal/storage/`
- `internal/services/`
- `tests/smoke/`
- `tests/integration/`

## Common Change Surfaces

- Echo route registration
- handlers and request binding
- `templ` views and fragments
- storage adapters
- app wiring in `cmd/server/main.go`

## Testing Expectations

- smoke test server boot plus one representative route
- integration tests against Docker-backed infra when handlers depend on databases, queues, or search
- verify rendered `templ` output when HTML fragments are contractually important

## Common Assistant Mistakes

- swapping in Chi-oriented assumptions
- placing all package logic in `main`
- treating rendered HTML as unimportant text instead of a contract surface

