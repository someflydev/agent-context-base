# Stack Router

Infer the active stack from repo signals, touched files, and user language.

## Primary Stack Signals

- `pyproject.toml`, `uv.lock`, `src/...`, `fastapi`
  - load `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `package.json`, `bun.lockb`, `bun.lock`, `hono`, `drizzle`, `tsx`, `src/routes/*.tsx`
  - load `context/stacks/typescript-hono-bun.md`
- `*.nimble`, `src/**/*.nim`, `jester`, `happyx`
  - load `context/stacks/nim-jester-happyx.md`
- `Cargo.toml`, `src/main.rs`, `axum`
  - load `context/stacks/rust-axum-modern.md`
- `go.mod`, `cmd/server/main.go`, `echo`, `.templ`
  - load `context/stacks/go-echo.md`
- `mix.exs`, `phoenix`, `lib/..._web/router.ex`, `lib/..._web/controllers`
  - load `context/stacks/elixir-phoenix.md`

## Storage And Infra Signals

- `redis`, `keydb`, `mongo`
  - load `context/stacks/redis-keydb-mongo.md`
- `duckdb`, `trino`, `polars`
  - load `context/stacks/duckdb-trino-polars.md`
- `nats`, `jetstream`
  - load `context/stacks/nats-jetstream.md`
- `meilisearch`
  - load `context/stacks/meilisearch.md`
- `timescaledb`
  - load `context/stacks/timescaledb.md`
- `elasticsearch`
  - load `context/stacks/elasticsearch.md`
- `qdrant`, `vector search`
  - load `context/stacks/qdrant.md`

## Deployment And Meta Signals

- `Procfile`, `app.json`, `dokku`, deployment wiring
  - load `context/stacks/dokku-conventions.md`
- task is about routing, prompts, manifests, templates, generated profiles, or repo bootstrap
  - load `context/stacks/prompt-first-repo.md`

## Routing Examples

- "Add a health route to my Bun app"
  - `context/stacks/typescript-hono-bun.md`
- "Add an HTMX fragment route to my Nim service"
  - `context/stacks/nim-jester-happyx.md`
- "Wire Qdrant for retrieval"
  - `context/stacks/qdrant.md`
- "Add a Phoenix release path for Dokku"
  - `context/stacks/elixir-phoenix.md`
  - `context/stacks/dokku-conventions.md`
- "Use Polars to reshape query output in FastAPI"
  - `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
  - `context/stacks/duckdb-trino-polars.md` if the change also touches analytical storage
- "Generate a new repo from this base"
  - `context/stacks/prompt-first-repo.md`
- "Wire a Qdrant-backed local index"
  - `context/stacks/qdrant.md`

## Guardrails

- load only the stacks on the active change path
- do not load every storage stack because a repo may support them eventually
- when two application stacks seem plausible, stop and resolve the dominant one
