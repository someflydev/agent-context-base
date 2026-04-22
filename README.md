# agent-context-base

`agent-context-base` is a context-first foundation for generating and running assistant-friendly repositories. It is not an app template and not a prompt dump. It is a system for keeping specs, validation rules, canonical examples, repo generation, and session startup narrow enough that long autonomous sessions stay trustworthy.

## Start Here By Goal

| Goal | Where to go |
| --- | --- |
| Understand this base repo | Read [`AGENT.md`](AGENT.md) → [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) → [`docs/ARCHITECTURE_MAP.md`](docs/ARCHITECTURE_MAP.md) |
| Generate a new repo | Read [`docs/usage/STARTING_NEW_PROJECTS.md`](docs/usage/STARTING_NEW_PROJECTS.md) → run `python scripts/new_repo.py` |
| Work inside a generated repo | Run `python3 .acb/scripts/work.py resume` → read `.acb/SESSION_BOOT.md` |
| Browse canonical examples | See [`examples/catalog.json`](examples/catalog.json) and [`verification/example_registry.yaml`](verification/example_registry.yaml) |
| Verify the repo | Run `python3 scripts/run_verification.py --tier fast` |

## What Problem It Solves

- Context loaded loosely causes assistant drift; this repo keeps canonical specs, validation rules, and routing in one narrow, loadable surface
- Later sessions rediscover repo intent from scratch; runtime continuity (`PLAN.md`, `TASK.md`, `SESSION.md`) makes session state visible and grounded
- Improvised patterns accumulate silently; canonical examples with enforced verification prevent drift at the pattern level
- Repo generation from templates is opaque; `.acb/` bundles make the generation contract explicit, inspectable, and diffable

See [`docs/repo-purpose.md`](docs/repo-purpose.md) for a full explanation of what this repo optimizes for and what it deliberately does not try to be.

## Canonical Examples

Fully implemented example families verified by `python3 scripts/run_verification.py --tier fast`. Browse via [`examples/catalog.json`](examples/catalog.json) and [`verification/example_registry.yaml`](verification/example_registry.yaml).

| Family | What It Shows | Languages / Stacks | Key Files |
|--------|--------------|-------------------|-----------|
| **canonical-api** | JSON, HTML fragment, data endpoint, faceted filter | Python/FastAPI, TypeScript/Hono/Bun, Go/Echo, Rust/Axum, Elixir/Phoenix, Scala/Tapir/ZIO, Kotlin/http4k/Exposed, Ruby/Hanami, Clojure/Kit, Crystal/Kemal, Dart/Dartfrog, OCaml/Dream, Nim/Jester, Zig/Zap+Jetzig (14 stacks) | `examples/canonical-api/` |
| **canonical-auth** | JWT/RBAC/multi-tenant backend auth | Python/PyJWT, TypeScript/jose, Go/golang-jwt, Rust/jsonwebtoken, Java/JJWT, Kotlin/JJWT, Ruby/ruby-jwt, Elixir/Joken (8 languages) | `examples/canonical-auth/` |
| **canonical-analytics** | Plotly+HTMX server-rendered charts (6 chart families) | Python/FastAPI/Jinja2, Go/Echo/templ, Rust/Axum/Askama, Elixir/Phoenix/HEEx (4 stacks) | `examples/canonical-analytics/` |
| **canonical-schema-validation** | Validation, contract generation, serialization (3 lanes, 18 examples) | Python, TypeScript, Go, Rust, Kotlin, Ruby, Elixir (7 languages) | `examples/canonical-schema-validation/` |
| **canonical-faker** | Synthetic data generation (TenantCore domain) | Python, JavaScript, Go, Rust, Java, Kotlin, Scala, Ruby, PHP, Elixir (10 languages) | `examples/canonical-faker/` |
| **canonical-terminal** | CLI tools, TUI apps, dual-mode CLI+TUI (14 examples, 2 per language) | Python (click+blessed, typer+textual), TypeScript (commander+ink, yargs+blessed), Go (cobra+bubbletea, urfave+tview), Rust (clap+ratatui, argh+tui-realm), Ruby (thor+tty, clamp+tty), Java (picocli+lanterna, jcommander+jline), Elixir (optionparser+owl, optimus+ratatouille) | `examples/canonical-terminal/` |
| **canonical-storage** | Storage pattern references | PostgreSQL, Redis, MongoDB, DuckDB+Parquet, DuckDB+Polars, MinIO/Parquet, NATS+MongoDB, Trino | `examples/canonical-storage/` |
| **canonical-multi-backend** | Polyglot service coordination | Duos and trios covering REST, gRPC, NATS JetStream, Kafka, RabbitMQ, NIFs | `examples/canonical-multi-backend/` |
| **canonical-dokku** | Dokku-deployable service stubs | Python/FastAPI, TypeScript/Hono/Bun, Go/Echo, Elixir/Phoenix | `examples/canonical-dokku/` |
| **canonical-rag** | Retrieval-augmented generation patterns | — | `examples/canonical-rag/` |
| **canonical-cli** | CLI-only tools (no TUI) | — | `examples/canonical-cli/` |
| **canonical-data-acquisition** | Data acquisition services | — | `examples/canonical-data-acquisition/` |
| **canonical-observability** | Observability patterns (metrics, tracing, logging) | — | `examples/canonical-observability/` |
| **canonical-integration-tests** | Integration test harness patterns | — | `examples/canonical-integration-tests/` |
| **canonical-smoke-tests** | Smoke test patterns | — | `examples/canonical-smoke-tests/` |
| **canonical-seed-data** | Seed data patterns | — | `examples/canonical-seed-data/` |
| **canonical-workflows** | Workflow orchestration patterns | — | `examples/canonical-workflows/` |
| **canonical-prompts** | Prompt authoring and iteration patterns | — | `examples/canonical-prompts/` |

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

Supporting infra packs cover Redis, MongoDB, DuckDB, DuckDB+Parquet, Trino, NATS JetStream, Kafka, RabbitMQ, Meilisearch, Elasticsearch, TimescaleDB, Qdrant, and MinIO. Additional stacks can be added by extending the router, manifest, example, and verification structure.

## Docs Index

### Architecture and design

- [`docs/ARCHITECTURE_MAP.md`](docs/ARCHITECTURE_MAP.md) — system map, arc statuses, directory index
- [`docs/architecture/ASSISTANT_RUNTIME_MODEL.md`](docs/architecture/ASSISTANT_RUNTIME_MODEL.md) — subsystem table, pipeline
- [`docs/architecture/CONTEXT_ENGINEERING_GUIDE.md`](docs/architecture/CONTEXT_ENGINEERING_GUIDE.md) — which artifact solves which problem
- [`docs/architecture-mental-model.md`](docs/architecture-mental-model.md) — companion diagrams (runtime, generation, verification, multi-agent)

### Operator usage

- [`docs/usage/STARTING_NEW_PROJECTS.md`](docs/usage/STARTING_NEW_PROJECTS.md) — new repo generation workflow and 100 example prompts
- [`docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md`](docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md) — long sessions, multi-agent, higher autonomy
- [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md) — `.acb/` composition and drift detection
- [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md) — normative behavior contract (MUST/SHOULD)
- [`docs/CONTRIBUTOR_PLAYBOOK.md`](docs/CONTRIBUTOR_PLAYBOOK.md) — how to extend stacks, examples, archetypes, verification

### Session startup and continuity

- [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) — deterministic startup contract + boot diagram
- [`docs/runtime-state-workflow.md`](docs/runtime-state-workflow.md) — PLAN/TASK/SESSION/MEMORY roles, checkpoint doctrine
- [`docs/startup-context-visibility.md`](docs/startup-context-visibility.md) — three-level startup visibility model
- [`docs/session-start.md`](docs/session-start.md) — quick-start checklist and commands
- [`docs/memory-layer-overview.md`](docs/memory-layer-overview.md) — memory artifact roles and decision flow

### Arc overviews (completed capability sets)

- [`docs/jwt-auth-arc-overview.md`](docs/jwt-auth-arc-overview.md) — JWT/RBAC arc (8 languages, verified)
- [`docs/plotly-htmx-arc-overview.md`](docs/plotly-htmx-arc-overview.md) — analytics arc (4 stacks)
- [`docs/faker-arc-overview.md`](docs/faker-arc-overview.md) — synthetic data arc (10 languages)
- [`docs/schema-validation-arc-overview.md`](docs/schema-validation-arc-overview.md) — validation arc (7 languages, 3 lanes)

### Reference

- [`docs/repo-purpose.md`](docs/repo-purpose.md) — what the repo optimizes for and first-class stacks
- [`docs/repo-layout.md`](docs/repo-layout.md) — directory roles
- [`docs/assistant-failure-modes.md`](docs/assistant-failure-modes.md) — failure taxonomy and mitigations
- [`docs/context-evolution.md`](docs/context-evolution.md) — changelog of architectural changes
- [`docs/terminal-validation-contract.md`](docs/terminal-validation-contract.md) — terminal example verification contract
- [`docs/terminal-web-parity.md`](docs/terminal-web-parity.md) — parity model between terminal and web examples
- [`docs/deployment-readiness-checklists.md`](docs/deployment-readiness-checklists.md) — deployment readiness checklists
- [`docs/schema-validation-drift-detection.md`](docs/schema-validation-drift-detection.md) — drift detection for schema-validation arc
- [`docs/jwt-auth-arc-prompt-pack.md`](docs/jwt-auth-arc-prompt-pack.md) — prompt pack for JWT auth arc
- [`docs/system-quick-reference.md`](docs/system-quick-reference.md) — quick operational reference after boot
- [`docs/system-self-explanation.md`](docs/system-self-explanation.md) — layer-by-layer explanation of the system

### Readiness assessments

- [`docs/public-example-backend-driven-ui-readiness.md`](docs/public-example-backend-driven-ui-readiness.md) — readiness self-assessment for backend-driven HTMX/Plotly example sets
- [`docs/public-example-data-systems-readiness.md`](docs/public-example-data-systems-readiness.md) — readiness self-assessment for data acquisition and data systems example sets
- [`docs/public-example-documentation-timing-readiness.md`](docs/public-example-documentation-timing-readiness.md) — readiness self-assessment for when a public example repo has earned its docs

## Verification Commands

```bash
python scripts/validate_context.py
python scripts/run_verification.py --tier fast
python scripts/acb_payload.py \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --manifest backend-api-fastapi-polars \
  --support-service postgres \
  --output-dir /tmp/analytics-api
```
