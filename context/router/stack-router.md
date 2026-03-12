# Stack Router

Purpose: infer the active technology stack from repo signals without over-reading the repository.

## Stack Inference Priority

1. `manifests/repo.profile.yaml`
2. explicit repo tool files and lockfiles
3. dominant source tree and framework entrypoints
4. current canonical examples already used in the repo
5. deployment/config files

If these disagree, stop and surface the mismatch.

## Primary Stack Signals

| Stack | Strong signals |
| --- | --- |
| `python-fastapi-polars-htmx-plotly` | `pyproject.toml`, `uv.lock`, `app/`, `src/`, `fastapi`, `polars`, `orjson` |
| `typescript-hono-bun-drizzle-tsx` | `bun.lockb`, `package.json`, `hono`, `drizzle`, `tsx`, `src/` |
| `rust-axum` | `Cargo.toml`, `src/main.rs`, `axum` |
| `go-echo-templ` | `go.mod`, `cmd/`, `internal/`, `echo`, `templ` |
| `elixir-phoenix` | `mix.exs`, `lib/`, `phoenix`, `heex` |
| `docker-compose-dokku` | `docker-compose.yml`, `docker-compose.test.yml`, `Dockerfile`, `Procfile`, Dokku app config |
| `redis-mongodb` | compose services, `redis`, `keydb`, `mongo`, storage adapters |
| `trino-duckdb-polars` | `duckdb`, `trino`, Polars pipelines, catalog config |
| `nats-jetstream-meilisearch` | `nats`, `jetstream`, `meilisearch`, queue/index clients |
| `timescaledb-elasticsearch-qdrant` | `timescaledb`, `elasticsearch`, `qdrant`, vector/time-series clients |
| `backend-extension-candidates` | repo profile or explicit adoption docs for Nim, Zig, Scala, Clojure, Kotlin, Crystal, OCaml, or Dart backends |

## Mixed-Stack Rule

Mixed stacks are allowed only when they are intentional and named in the repo profile. Example:

- FastAPI API plus Qdrant
- Hono service plus Redis
- Prompt-first repo plus polyglot lab

Do not load sibling backend stacks just because they exist in the base repo.

## Default Stack Bundles

| If task mentions | Load |
| --- | --- |
| FastAPI, uv, ruff, polars, HTMX, Plotly | `context/stacks/python-fastapi-polars-htmx-plotly.md` |
| Hono, Bun, Drizzle, TSX, HTMX | `context/stacks/typescript-hono-bun-drizzle-tsx.md` |
| Axum, Cargo | `context/stacks/rust-axum.md` |
| Echo, templ, Go | `context/stacks/go-echo-templ.md` |
| Phoenix, mix, LiveView | `context/stacks/elixir-phoenix.md` |
| Redis, KeyDB, MongoDB | `context/stacks/redis-mongodb.md` |
| DuckDB, Trino, Polars | `context/stacks/trino-duckdb-polars.md` |
| NATS, Jetstream, Meilisearch | `context/stacks/nats-jetstream-meilisearch.md` |
| TimescaleDB, Elasticsearch, Qdrant | `context/stacks/timescaledb-elasticsearch-qdrant.md` |
| Dokku, Compose, Dockerfile, Procfile | `context/stacks/docker-compose-dokku.md` |

## Stack Stop Conditions

Stop when:

- two backend stacks both appear active for the same service
- the user asks for a stack not represented in the repo profile or stack docs
- generated code would cross from one stack's conventions into another's without an explicit bridge
