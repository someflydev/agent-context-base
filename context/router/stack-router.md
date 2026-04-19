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
- `jinja2`, `Jinja2`, `TemplateResponse`, Python + HTMX + Tailwind rendering
  - load `context/stacks/python-fastapi-jinja2-htmx-plotly.md`
- `go.mod`, `echo`, `templ`, `.templ`, Go server-rendered HTMX analytics
  - load `context/stacks/go-echo-templ-htmx-plotly.md`
- `Cargo.toml`, `askama`, Rust server-rendered HTMX analytics
  - load `context/stacks/rust-axum-askama-htmx-plotly.md`
- `mix.exs`, Phoenix controllers (non-LiveView), `HX-Request`, Elixir HTMX analytics
  - load `context/stacks/elixir-phoenix-htmx-plotly.md`

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
- `duckdb` plus `parquet`, `duckdb.read_parquet`, local parquet scan, hive partition directory pattern without MinIO or Trino
  - load `context/stacks/duckdb-parquet.md`
  - load `context/stacks/parquet.md`
- `duckdb` or `polars` without trino
  - load primary application stack; load `context/stacks/duckdb-trino-polars.md` only if trino is also present
- `postgresql`, `postgres`, `jsonb`, `materialized view`, migration-heavy SQL, transactional SQL baseline
  - load `context/stacks/postgresql.md`
- `parquet`, `arrow schema`, `row group`, `snappy`, `zstandard`, `pyarrow schema`
  - load `context/stacks/parquet.md`
- `minio`, `s3-compatible`, `object store`, `bucket` without AWS context
  - load `context/stacks/minio.md`
- `parquet` plus `minio`, `data lake write path`, `write parquet to object store`
  - load `context/stacks/parquet-minio.md`
  - load `context/stacks/parquet.md`
  - load `context/stacks/minio.md`
- `nats`, `nats jetstream`, `jetstream`, `nats subject`, `durable consumer`
  - load `context/stacks/nats-jetstream.md`
- `nats` plus `mongo`, `capture-enrich-persist`, `publish to nats then insert to mongo`
  - load `context/stacks/nats-jetstream-mongo.md`
  - load `context/stacks/nats-jetstream.md`
  - load `context/stacks/mongo.md`
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
- "Write partitioned Parquet to MinIO"
  - `context/stacks/parquet-minio.md`
  - `context/stacks/parquet.md`
  - `context/stacks/minio.md`
- "Read Parquet from MinIO with DuckDB"
  - `context/stacks/parquet-minio.md`
  - `context/stacks/duckdb-trino-polars.md`
- "Add MinIO bucket to the dev docker-compose"
  - `context/stacks/minio.md`
- "Set up NATS JetStream for request capture"
  - `context/stacks/nats-jetstream.md`
- "Publish request/response events to NATS then enrich and insert to MongoDB"
  - `context/stacks/nats-jetstream-mongo.md`
- "Add dead letter handling to the NATS consumer"
  - `context/stacks/nats-jetstream.md`
- "Write the enriched documents to a weekly MongoDB collection"
  - `context/stacks/nats-jetstream-mongo.md`
  - `context/stacks/mongo.md`
- "Use Polars to reshape query output in FastAPI"
  - `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
  - `context/stacks/duckdb-trino-polars.md` if the change also touches analytical storage
- "Generate a new repo from this base"
  - `context/stacks/prompt-first-repo.md`
  - prefer `scripts/new_repo.py` with the operator prompt preserved into `.prompts/initial-prompt.txt`
- "Don’t give me Python-only guidance for this sync pipeline"
  - dominant app stack
  - `examples/canonical-data-acquisition/README.md`
  - `context/doctrine/data-acquisition-invariants.md`
- "Wire a Qdrant-backed local index"
  - `context/stacks/qdrant.md`
- "How do I add JWT auth to my FastAPI app?"
  - `context/stacks/python-fastapi-pyjwt-rbac.md`
  # added by PROMPT_134
- "Show me RBAC with JWT in Go"
  - `context/stacks/go-echo-golang-jwt-rbac.md`
  # added by PROMPT_134
- "How do I verify a JWT in Rust / Axum?"
  - `context/stacks/rust-axum-jsonwebtoken-rbac.md`
  # added by PROMPT_134
- "Show me Hono JWT auth with jose"
  - `context/stacks/typescript-hono-jose-rbac.md`
  # added by PROMPT_134
- "Show me Spring Boot JWT auth with JJWT"
  - `context/stacks/java-spring-jjwt-rbac.md`
  # added by PROMPT_134
- "Show me Kotlin http4k JWT auth"
  - `context/stacks/kotlin-http4k-jjwt-rbac.md`
  # added by PROMPT_134
- "Show me Hanami JWT auth"
  - `context/stacks/ruby-hanami-ruby-jwt-rbac.md`
  # added by PROMPT_134
- "Show me Phoenix JWT auth with Joken"
  - `context/stacks/elixir-phoenix-joken-rbac.md`
  # added by PROMPT_134

## Terminal Stacks

| Language | Tier | CLI Lib | TUI Lib | Stack file | Canonical example |
|----------|------|---------|---------|------------|-------------------|
| Python | dual-mode | typer | textual | `context/stacks/terminal-python-typer-textual.yaml` | `examples/canonical-terminal/python-typer-textual/` |
| Python | cli-plus-light-tui | click | blessed | `context/stacks/terminal-python-click-blessed.yaml` | `examples/canonical-terminal/python-click-blessed/` |
| Rust | dual-mode | clap | ratatui | `context/stacks/terminal-rust-clap-ratatui.yaml` | `examples/canonical-terminal/rust-clap-ratatui/` |
| Rust | dual-mode | argh | tui-realm | `context/stacks/terminal-rust-argh-tui-realm.yaml` | `examples/canonical-terminal/rust-argh-tui-realm/` |
| Go | dual-mode | cobra | bubbletea | `context/stacks/terminal-go-cobra-bubbletea.yaml` | `examples/canonical-terminal/go-cobra-bubbletea/` |
| Go | dual-mode | urfave/cli | tview | `context/stacks/terminal-go-urfave-tview.yaml` | `examples/canonical-terminal/go-urfave-tview/` |
| TypeScript | dual-mode | commander | ink | `context/stacks/terminal-typescript-commander-ink.yaml` | `examples/canonical-terminal/typescript-commander-ink/` |
| TypeScript | cli-plus-light-tui | yargs | blessed | `context/stacks/terminal-typescript-yargs-blessed.yaml` | `examples/canonical-terminal/typescript-yargs-blessed/` |
| Java | dual-mode | picocli | lanterna | `context/stacks/terminal-java-picocli-lanterna.yaml` | `examples/canonical-terminal/java-picocli-lanterna/` |
| Java | cli-plus-interactive-shell | jcommander | jline | `context/stacks/terminal-java-jcommander-jline.yaml` | `examples/canonical-terminal/java-jcommander-jline/` |
| Ruby | guided-interactive-cli | thor | tty-prompt | `context/stacks/terminal-ruby-thor-tty.yaml` | `examples/canonical-terminal/ruby-thor-tty/` |
| Ruby | cli-plus-raw-input | clamp | tty-reader | `context/stacks/terminal-ruby-clamp-tty.yaml` | `examples/canonical-terminal/ruby-clamp-tty/` |
| Elixir | dual-mode | optimus | ratatouille | `context/stacks/terminal-elixir-optimus-ratatouille.yaml` | `examples/canonical-terminal/elixir-optimus-ratatouille/` |
| Elixir | cli-plus-rich-output | optionparser (built-in) | owl | `context/stacks/terminal-elixir-optionparser-owl.yaml` | `examples/canonical-terminal/elixir-optionparser-owl/` |

See `examples/canonical-terminal/DECISION_GUIDE.md` (PROMPT_106) for deeper
stack selection guidance.

## Schema Validation

- `schema-validation-python`
  - Pydantic, marshmallow, runtime + contract lane
- `schema-validation-typescript`
  - Zod, Valibot, io-ts, TypeBox + Ajv; hybrid + contract lanes
- `schema-validation-go`
  - go-playground/validator, ozzo-validation; runtime + external contract
- `schema-validation-rust`
  - validator, garde, serde + schemars; runtime + contract lanes
- `schema-validation-kotlin`
  - Konform, Hibernate Validator; runtime + JVM contract path
- `schema-validation-ruby`
  - dry-validation, dry-schema; runtime + schema lane
- `schema-validation-elixir`
  - Ecto.Changeset, Norm, ex_json_schema; runtime + contract lane

## Faker And Synthetic Data

- `faker-python`
  - `context/stacks/faker-python.yaml`
- `faker-javascript`
  - `context/stacks/faker-javascript.yaml`
- `faker-go`
  - `context/stacks/faker-go.yaml`
- `faker-rust`
  - `context/stacks/faker-rust.yaml`
- `faker-java`
  - `context/stacks/faker-java.yaml`
- `faker-kotlin`
  - `context/stacks/faker-kotlin.yaml`
- `faker-scala`
  - `context/stacks/faker-scala.yaml`
- `faker-ruby`
  - `context/stacks/faker-ruby.yaml`
- `faker-php`
  - `context/stacks/faker-php.yaml`
- `faker-elixir`
  - `context/stacks/faker-elixir.yaml`

## JWT Auth, RBAC, And Multi-Tenant Backend Patterns

- `python-fastapi-pyjwt-rbac`
  - `context/stacks/python-fastapi-pyjwt-rbac.md`
- `typescript-hono-jose-rbac`
  - `context/stacks/typescript-hono-jose-rbac.md`
- `go-echo-golang-jwt-rbac`
  - `context/stacks/go-echo-golang-jwt-rbac.md`
- `rust-axum-jsonwebtoken-rbac`
  - `context/stacks/rust-axum-jsonwebtoken-rbac.md`
- `java-spring-jjwt-rbac`
  - `context/stacks/java-spring-jjwt-rbac.md`
- `kotlin-http4k-jjwt-rbac`
  - `context/stacks/kotlin-http4k-jjwt-rbac.md`
- `ruby-hanami-ruby-jwt-rbac`
  - `context/stacks/ruby-hanami-ruby-jwt-rbac.md`
- `elixir-phoenix-joken-rbac`
  - `context/stacks/elixir-phoenix-joken-rbac.md`

## Guardrails

- load only the stacks on the active change path
- do not load every storage stack because a repo may support them eventually
- when two application stacks seem plausible, stop and resolve the dominant one
