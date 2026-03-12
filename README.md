# agent-context-base

`agent-context-base` is a reusable foundation for future repos. It is designed for prompt-first work, small context bundles, deterministic routing, and practical repo bootstrap across Codex, Claude, and Gemini.

This repo is not a product app. It is a base system for future project repos that need:

- strong `AGENT.md` and `CLAUDE.md` routing
- doctrine separated from workflows, stacks, archetypes, examples, manifests, and templates
- task inference from normal language instead of memorized internal names
- canonical examples before ad hoc patterns
- smoke-test-heavy delivery backed by minimal real-infra integration tests for meaningful boundaries
- Docker-backed dev and test isolation
- Dokku-oriented deployment conventions
- a real starter bootstrap script instead of copy-paste repo assembly

## Start Here

Read in this order:

1. `AGENT.md` or `CLAUDE.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `context/router/task-router.md`

Then load only the smallest bundle that matches the task:

- core doctrine relevant to the change
- one primary workflow
- one archetype
- the needed stack packs
- one preferred canonical example

## What v2 Adds

The second pass adds:

- actual canonical example files under `examples/`, not README placeholders only
- richer manifest files with routing, bootstrap, Compose, and support metadata
- `scripts/new_repo.py` for deterministic repo bootstrap
- stronger alignment between manifests, routers, aliases, templates, and examples
- starter templates for Compose, Dokku, prompt-first prompts, profile summaries, smoke tests, integration tests, and seed data

## First-Class Coverage

The base now gives explicit support to:

- Python with FastAPI, `uv`, Ruff, `orjson`, and Polars
- TypeScript with Hono, Bun, Drizzle ORM, and TSX
- Rust with Axum
- Go with Echo and templ
- Elixir with Phoenix
- Redis or KeyDB, MongoDB, DuckDB, Trino, NATS JetStream, Meilisearch, TimescaleDB, Elasticsearch, and Qdrant
- prompt-first repo workflows and Dokku deployment conventions

It also leaves clean extension space for additional stacks such as Nim, Zig, Scala, Clojure, Kotlin, Crystal, OCaml, and Dart without forcing them into the initial file set.

## Repository Shape

- `docs/`: repo-level purpose and layout
- `context/doctrine/`: stable rules and philosophy
- `context/workflows/`: task playbooks
- `context/stacks/`: stack-specific guidance
- `context/archetypes/`: project-shape guidance
- `context/router/`: routing rules and alias mapping
- `context/skills/`: short reusable assistant capabilities
- `manifests/`: machine-readable context bundles
- `examples/`: canonical example strategy surfaces
- `templates/`: starter scaffolds, not canonical implementations
- `scripts/`: lightweight repo utilities
- `smoke-tests/`: doctrine for future smoke-test suites

## Bootstrap Flow

Use `scripts/new_repo.py` when you want a first-pass descendant repo:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --dokku
```

That script renders a starter README, `AGENT.md`, `CLAUDE.md`, `.gitignore`, generated profile files, optional prompt files, and isolated Compose layouts with repo-derived names.

## Intent

Future repos should copy from this base selectively, then specialize with project-local manifests, examples, smoke tests, and deployment details. The base should stay composable, strict, and easy for both humans and coding assistants to navigate.
