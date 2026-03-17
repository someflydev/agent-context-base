# Repo Purpose

`agent-context-base` is a foundation for repositories that will be built with coding assistants, not a finished application and not a generic starter app.

Its job is to make assistant behavior more reliable by separating the repository into a few clear layers:

- doctrine: durable rules and guardrails
- workflows: task playbooks
- stacks: implementation guidance for frameworks and infra
- archetypes: project-shape guidance
- manifests: machine-readable context bundles
- canonical examples: preferred completed patterns
- templates: starter scaffolds for generated repos
- continuity artifacts: `MEMORY.md`, stop hooks, and handoff snapshots

## What This Repo Optimizes For

- small, high-signal context bundles
- natural-language routing instead of memorized filenames
- canonical examples before improvised patterns
- smoke-test-heavy delivery with minimal real-infra tests where boundaries matter
- isolated dev and test Compose layouts
- prompt-first repo generation and long-lived assistant workflows

## What It Does Not Try To Be

- a product codebase
- a repo factory with hidden abstractions
- a replacement for project-specific manifests and examples
- a place to dump every framework detail into one document
- a substitute for code inspection, tests, or task-local continuity notes

## Supported Project Shapes

- Prompt-first repos
- Backend API services
- CLI tools
- Data pipelines
- Data acquisition services
- Multi-backend services
- Multi-source sync platforms
- Local RAG systems
- Multi-storage experiments
- Polyglot labs
- Dokku-deployable services

## First-Class Stacks

The most developed stacks in this base are:

- Python / FastAPI / `uv` / Ruff / `orjson` / Polars
- TypeScript / Hono / Bun / Drizzle
- Rust / Axum
- Go / Echo / templ
- Elixir / Phoenix
- Scala / Tapir / http4s / ZIO
- Kotlin / http4k / Exposed
- Nim / Jester / HappyX
- Clojure / Kit / next.jdbc / Hiccup
- Dart / Dartfrog
- OCaml / Dream / Caqti / Tyxml
- Crystal / Kemal / Avram
- Zig / Zap / Jetzig
- Ruby / Hanami

Supporting infra packs cover systems such as Redis, MongoDB, DuckDB, DuckDB+Parquet, Trino, NATS JetStream, Kafka, RabbitMQ, Meilisearch, Elasticsearch, TimescaleDB, Qdrant, and MinIO. Additional stacks can be added by extending the same router, manifest, example, and verification structure.
