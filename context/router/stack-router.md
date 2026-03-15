# Stack Router

Infer the active stack from repo signals, touched files, and user language.

## Primary Stack Signals

- `pyproject.toml`, `uv.lock`, `src/...`, `fastapi`
  - load `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `package.json`, `bun.lockb`, `bun.lock`, `hono`, `drizzle`, `tsx`, `src/routes/*.tsx`
  - load `context/stacks/typescript-hono-bun.md`
- `*.nimble`, `src/**/*.nim`, `jester`, `happyx`
  - load `context/stacks/nim-jester-happyx.md`
- `shard.yml`, `src/**/*.cr`, `kemal`, `avram`
  - load `context/stacks/crystal-kemal-avram.md`
- `build.sbt`, `project/*.scala`, `src/main/scala/**/*.scala`, `tapir`, `http4s`, `zio`
  - load `context/stacks/scala-tapir-http4s-zio.md`
- `build.gradle.kts`, `settings.gradle.kts`, `src/main/kotlin/**/*.kt`, `http4k`, `exposed`
  - load `context/stacks/kotlin-http4k-exposed.md`
- `pubspec.yaml`, `routes/**/*.dart`, `dart_frog`
  - load `context/stacks/dart-dartfrog.md`
- `deps.edn`, `src/**/*.clj`, `kit`, `next.jdbc`, `hiccup`
  - load `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `dune-project`, `*.opam`, `bin/**/*.ml`, `lib/**/*.ml`, `dream`, `caqti`, `tyxml`
  - load `context/stacks/ocaml-dream-caqti-tyxml.md`
- `build.zig`, `build.zig.zon`, `src/main.zig`, `zap`, `jetzig`
  - load `context/stacks/zig-zap-jetzig.md`
- `Cargo.toml`, `src/main.rs`, `axum`
  - load `context/stacks/rust-axum-modern.md`
- `go.mod`, `cmd/server/main.go`, `echo`, `.templ`
  - load `context/stacks/go-echo.md`
- `mix.exs`, `phoenix`, `lib/..._web/router.ex`, `lib/..._web/controllers`
  - load `context/stacks/elixir-phoenix.md`
- `Gemfile`, `config.ru`, `app/router.rb`, `app/actions/**/*.rb`, `hanami`
  - load `context/stacks/ruby-hanami.md`

## Storage And Infra Signals

- `sources/`, `parsers/`, `archive/raw/`, `httpx`, `beautifulsoup`, `playwright`, `selectors`
  - load `context/stacks/scraping-and-ingestion-patterns.md`
- `source_research`, `source_scorecard`, `licensing`, `robots`, `dataset evaluation`
  - load `context/stacks/source-research-and-evaluation.md`
- `events/`, `scheduler/`, `sync.requested`, `sync.failed`, `outbox`
  - load `context/stacks/event-streaming-patterns.md`
- `redis` or `keydb` alone
  - load `context/stacks/redis.md`
- `mongo`, `mongodb`, `aggregation pipeline`, `partialFilterExpression`
  - load `context/stacks/mongo.md`
- `redis` plus `mongo`, `keydb`, or mixed cache-plus-document-store patterns
  - load `context/stacks/redis-keydb-mongo.md`
- `trino`, `federated analytics`, cross-catalog query, cross-database query
  - load `context/stacks/trino.md`
- `duckdb` plus `trino` plus `polars`, local analytical pipeline with cross-source federation
  - load `context/stacks/duckdb-trino-polars.md`
- `duckdb` or `polars` without trino
  - load primary application stack; load `context/stacks/duckdb-trino-polars.md` only if trino is also present
- `postgresql`, `postgres`, `jsonb`, `materialized view`, migration-heavy SQL, transactional SQL baseline
  - load `context/stacks/postgresql.md`
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
- task is about HTMX fragments, Tailwind server-rendered filters, Plotly query endpoints, faceted counts, or Playwright verification of backend-generated UI
  - load `context/stacks/backend-driven-ui-htmx-tailwind-plotly.md`

## Routing Examples

- "Add a health route to my Bun app"
  - `context/stacks/typescript-hono-bun.md`
- "Add an HTMX fragment route to my Nim service"
  - `context/stacks/nim-jester-happyx.md`
- "Add a Kemal endpoint or Avram query to my Crystal service"
  - `context/stacks/crystal-kemal-avram.md`
- "Add a typed Tapir route to my Scala service"
  - `context/stacks/scala-tapir-http4s-zio.md`
- "Add an Exposed-backed endpoint to my Kotlin service"
  - `context/stacks/kotlin-http4k-exposed.md`
- "Add a JSON, fragment, or chart endpoint to my Dart Frog service"
  - `context/stacks/dart-dartfrog.md`
- "Add a Kit route or Hiccup fragment to my Clojure service"
  - `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- "Add a Dream endpoint or TyXML fragment to my OCaml service"
  - `context/stacks/ocaml-dream-caqti-tyxml.md`
- "Add a JSON or fragment endpoint to my Zig service"
  - `context/stacks/zig-zap-jetzig.md`
- "Wire Qdrant for retrieval"
  - `context/stacks/qdrant.md`
- "Add backoff and rate-limit awareness for source ingestion"
  - `context/stacks/scraping-and-ingestion-patterns.md`
- "Give me the Go version of the acquisition example"
  - `context/stacks/go-echo.md`
  - `examples/canonical-data-acquisition/README.md`
  - `context/doctrine/data-acquisition-invariants.md`
- "Research candidate public data sources and compare tradeoffs"
  - `context/stacks/source-research-and-evaluation.md`
- "What is the Rust canonical example for raw archive plus normalization?"
  - `context/stacks/rust-axum-modern.md`
  - `examples/canonical-data-acquisition/README.md`
  - `context/doctrine/data-acquisition-invariants.md`
- "Coordinate source syncs with events"
  - `context/stacks/event-streaming-patterns.md`
  - `context/stacks/nats-jetstream.md` if JetStream is the concrete broker
- "Add a Phoenix release path for Dokku"
  - `context/stacks/elixir-phoenix.md`
  - `context/stacks/dokku-conventions.md`
- "Add a JSON, fragment, or chart endpoint to my Hanami service"
  - `context/stacks/ruby-hanami.md`
- "Add HTMX filters with exact counts to my backend"
  - dominant app stack
  - `context/stacks/backend-driven-ui-htmx-tailwind-plotly.md`
- "Verify a backend-generated filter UI with Playwright"
  - dominant app stack
  - `context/stacks/backend-driven-ui-htmx-tailwind-plotly.md`
- "Build a Redis leaderboard"
  - `context/stacks/redis.md`
- "Add expiring cache keys for session tokens"
  - `context/stacks/redis.md`
- "Add weekly MongoDB request log reporting"
  - `context/stacks/mongo.md`
- "Add a MongoDB aggregation pipeline for weekly summaries"
  - `context/stacks/mongo.md`
- "Query Postgres and Mongo together with Trino"
  - `context/stacks/trino.md`
  - `context/stacks/postgresql.md`
  - `context/stacks/mongo.md`
- "Add a materialized-view-backed reporting path in PostgreSQL"
  - `context/stacks/postgresql.md`
- "Use TimescaleDB rollups on top of PostgreSQL"
  - `context/stacks/timescaledb.md`
  - `context/stacks/postgresql.md`
- "Wire Redis as a cache layer in front of MongoDB"
  - `context/stacks/redis-keydb-mongo.md`
- "Use Polars to reshape query output in FastAPI"
  - `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
  - `context/stacks/duckdb-trino-polars.md` if the change also touches analytical storage
- "Generate a new repo from this base"
  - `context/stacks/prompt-first-repo.md`
- "Don’t give me Python-only guidance for this sync pipeline"
  - dominant app stack
  - `examples/canonical-data-acquisition/README.md`
  - `context/doctrine/data-acquisition-invariants.md`
- "Wire a Qdrant-backed local index"
  - `context/stacks/qdrant.md`

## Guardrails

- load only the stacks on the active change path
- do not load every storage stack because a repo may support them eventually
- when two application stacks seem plausible, stop and resolve the dominant one
