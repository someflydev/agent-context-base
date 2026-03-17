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

## Tool Setup

**Minimum Go version: 1.24** (required for the `-tool` flag approach).

One-time setup — install `templ` as a project-scoped tool (no global install):

```bash
go get -tool github.com/a-h/templ/cmd/templ@latest
```

Running `templ` and tests:

```bash
go tool templ generate          # generate .go files from .templ sources
go test ./...                   # run all tests
go vet ./...                    # static analysis
```

To add Playwright e2e tests (playwright-go):

```bash
go get github.com/playwright-community/playwright-go
go run github.com/playwright-community/playwright-go/cmd/playwright install --with-deps chromium
go test ./tests/e2e/...
```

Never use `go install github.com/a-h/templ/cmd/templ` — it writes to `$GOPATH/bin` and causes
version drift. Always use `go get -tool` and `go tool templ`. See
`context/doctrine/tool-invocation-discipline.md`.

## Common Assistant Mistakes

- swapping in Chi-oriented assumptions
- placing all package logic in `main`
- treating rendered HTML as unimportant text instead of a contract surface

