# Repo Purpose

`agent-context-base` exists to help future repositories start with a strong, consistent assistant-facing structure.

## What This Repo Provides

- routing entrypoints for Codex, Claude, and similar coding assistants
- doctrine separated from execution playbooks
- first-class stack packs for the stacks used most often
- archetype packs for common project shapes
- manifest files that can drive validation and context preview tooling
- canonical example strategy surfaces
- starter templates for repo bootstrap work
- lightweight scripts for checking the structure

## What This Repo Does Not Try To Be

- a finished application
- a giant forever-monorepo
- a substitute for project-specific manifests and examples
- a place to dump every possible stack detail into one file

## Operating Assumptions

- work is prompt-first
- humans should not need to memorize internal routing names
- canonical examples are preferable to ad hoc pattern mixing
- smoke tests are required often, but significant boundaries also need minimal real-infra integration tests
- Docker-backed dev and test environments should be isolated by default
- Dokku is a practical deployment target for many future service repos
- the base should stay inspectable through small scripts and machine-readable metadata rather than a repo-factory abstraction layer

## First-Class v1 Project Shapes

This base is optimized for:

- prompt-first meta repos
- backend API services
- CLI tools
- data pipelines
- local RAG systems
- multi-storage experiments
- Dokku-deployable services

## First-Class v1 Stacks

This base intentionally gives better detail to the stacks used most often:

- FastAPI plus `uv`, Ruff, `orjson`, and Polars
- Hono plus Bun, Drizzle ORM, and TSX
- Axum
- Echo plus templ
- Phoenix
- Redis or KeyDB, MongoDB, DuckDB, Trino, NATS JetStream, Meilisearch, TimescaleDB, Elasticsearch, and Qdrant

Other backend stacks should extend the same structure instead of forcing their full treatment into v1.

Legible extension paths currently include Nim with Jester or HappyX, Zig with Zap or Jetzig, Scala with Tapir or http4s or ZIO, Clojure with Kit or next.jdbc or Hiccup, Kotlin with http4k or Exposed, Crystal with Kemal or Avram, OCaml with Dream or Caqti or TyXML, and Dart with Dart Frog.
