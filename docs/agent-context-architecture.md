# Agent-Oriented Context Architecture

## SECTION 1 - Design principles

### Why giant `AGENT.md` and `CLAUDE.md` files are insufficient

Giant router files fail because they mix durable doctrine, stack details, task steps, examples, and exceptions into one surface. Frontier models then:

- over-read irrelevant instructions
- blend conflicting patterns
- miss the actual active stack
- carry stale rules forward because everything looks equally important

Top-level agent files should be routers, not encyclopedias.

### Why context should be layered

Layering separates stable truth from changeable execution details:

- doctrine: durable repo philosophy and invariants
- workflows: task sequences
- archetypes: repo-shape expectations
- stacks: language/framework specifics
- examples: canonical reference implementations
- manifests: machine-readable routing metadata
- templates: starting points for new repos or modules

This reduces token load and makes updates local rather than repo-wide.

### How doctrine, skills, workflows, stacks, archetypes, templates, and examples differ

| Layer | Purpose | Stability | Typical question answered |
| --- | --- | --- | --- |
| doctrine | durable rules and preferences | high | "What do we believe and enforce?" |
| skills | reusable specialized operating knowledge | medium-high | "What narrow capability pack should be applied?" |
| workflows | task execution sequences | medium | "How do I perform this change safely?" |
| stacks | technology-specific conventions | medium | "How does this language/framework repo behave?" |
| archetypes | repo-shape patterns | medium-high | "What kind of repo is this?" |
| templates | bootstrap scaffolds | medium | "What should a new instance start from?" |
| examples | canonical solved patterns | medium-low | "What concrete implementation should I imitate?" |
| manifests | routing metadata | high | "What should I load first?" |

### Why canonical examples matter

Frontier models imitate local patterns better than they infer abstract policy. Canonical examples:

- collapse ambiguity into one preferred pattern
- reduce invention pressure
- provide file placement, naming, and test shape at once
- make cross-model behavior more consistent

Examples are often more operationally valuable than prose doctrine when both exist.

### How to reduce context bloat without under-specifying the task

Use a deterministic loading sequence:

1. repo profile
2. routing files
3. only the doctrine docs required by the task
4. one workflow
5. one archetype pack
6. only the active stack packs
7. the smallest canonical example set

Avoid free-form scanning until a stop condition is hit.

## SECTION 2 - Folder structure options

### Option A: Flat Pack Library

```text
.
├── AGENT.md
├── CLAUDE.md
├── docs/
├── context/
│   ├── doctrine/
│   ├── skills/
│   ├── workflows/
│   ├── stacks/
│   ├── archetypes/
│   └── examples/
└── manifests/
```

Best when:

- one repo family has limited stack variation
- human maintainers want very simple navigation

Tradeoffs:

- easy to understand
- weak deterministic routing unless manifests are strong
- examples tend to sprawl into the wrong folders

Failure modes:

- `context/stacks/` becomes a junk drawer
- agent loads too many sibling files because structure is shallow

Model fit:

- Codex: good if manifests are precise
- Claude: fine, but may over-read without strong router guidance
- Gemini: acceptable, but needs stronger metadata cues

### Option B: Stack-First Matrix

```text
.
├── context/
│   ├── python-fastapi/
│   │   ├── doctrine/
│   │   ├── workflows/
│   │   └── examples/
│   ├── ts-hono/
│   ├── go-echo/
│   └── rust-axum/
└── manifests/
```

Best when:

- one organization has many repos but each repo is dominated by one stack

Tradeoffs:

- strong stack locality
- weak archetype reuse
- cross-stack doctrine duplicates fast

Failure modes:

- prompt-first or multi-storage repos do not fit cleanly
- doctrine drifts across stack folders

Model fit:

- Codex: efficient for single-stack repos
- Claude: good for direct stack lookup
- Gemini: workable but brittle for mixed-stack repos

### Option C: Manifest-First Bundle Store

```text
.
├── AGENT.md
├── CLAUDE.md
├── manifests/
│   ├── repo.profile.yaml
│   ├── bundles/
│   ├── tasks/
│   ├── stacks/
│   └── archetypes/
├── context/
└── examples/
```

Best when:

- automation and machine-assisted loading are the primary goal

Tradeoffs:

- deterministic and scriptable
- less friendly for human browsing
- metadata upkeep becomes real work

Failure modes:

- manifests become stale
- humans stop trusting routing because bundles point at outdated files

Model fit:

- Codex: excellent if manifests are current
- Claude: good when paired with human-readable routers
- Gemini: strong because metadata is explicit

### Option D: Hybrid Layered Router (recommended)

```text
.
├── AGENT.md
├── CLAUDE.md
├── README.md
├── docs/
├── context/
│   ├── doctrine/
│   ├── skills/
│   ├── workflows/
│   ├── stacks/
│   ├── archetypes/
│   └── router/
├── manifests/
├── examples/
├── templates/
├── scripts/
└── smoke-tests/
```

Best when:

- repos vary by archetype and stack
- prompt-first and software repos must share a mental model
- future automation matters but humans still need clarity

Tradeoffs:

- slightly more structure to maintain
- needs discipline around manifests and canonical examples

Failure modes:

- router files become too verbose
- examples and templates get confused
- stacks proliferate without an owner

Model fit:

- Codex: best balance of deterministic routing and minimal load
- Claude: best if routers stay concise and delegated
- Gemini: best when manifests reinforce folder semantics

## SECTION 3 - Recommended final architecture

Recommended for your workflows: the Hybrid Layered Router.

It matches prompt-first repo thinking, polyglot extensibility, canonical-example reuse, and future manifest-driven automation.

```text
.
├── AGENT.md
├── CLAUDE.md
├── README.md
├── docs/
│   ├── agent-context-architecture.md
│   ├── operator-manual.md
│   └── repo-bootstrap-checklist.md
├── context/
│   ├── doctrine/
│   │   ├── 00-core-principles.md
│   │   ├── 01-naming-and-clarity.md
│   │   ├── 02-testing-philosophy.md
│   │   ├── 03-smoke-test-philosophy.md
│   │   ├── 04-compose-port-isolation.md
│   │   ├── 05-commit-hygiene.md
│   │   ├── 06-documentation-philosophy.md
│   │   ├── 07-prompt-first-conventions.md
│   │   ├── 08-canonical-example-policy.md
│   │   ├── 09-context-loading-rules.md
│   │   └── 10-deployment-dokku-thinking.md
│   ├── skills/
│   │   ├── README.md
│   │   ├── canonical-example-curator.md
│   │   └── manifest-maintainer.md
│   ├── workflows/
│   │   ├── add-feature.md
│   │   ├── fix-bug.md
│   │   ├── refactor.md
│   │   ├── add-smoke-tests.md
│   │   ├── bootstrap-repo.md
│   │   ├── generate-prompt-sequence.md
│   │   ├── post-flight-refinement.md
│   │   ├── add-deployment-support.md
│   │   ├── add-seed-data.md
│   │   ├── add-api-endpoint.md
│   │   ├── extend-cli.md
│   │   ├── add-local-rag-indexing.md
│   │   └── add-storage-integration.md
│   ├── stacks/
│   │   ├── python-fastapi-polars-htmx-plotly.md
│   │   ├── typescript-hono-bun-drizzle-tsx.md
│   │   ├── go-echo-templ.md
│   │   ├── rust-axum.md
│   │   ├── elixir-phoenix.md
│   │   ├── docker-compose-dokku.md
│   │   ├── redis-mongodb.md
│   │   ├── trino-duckdb-polars.md
│   │   ├── nats-jetstream-meilisearch.md
│   │   ├── timescaledb-elasticsearch-qdrant.md
│   │   └── backend-extension-candidates.md
│   ├── archetypes/
│   │   ├── prompt-first-repo.md
│   │   ├── backend-api.md
│   │   ├── cli-tool.md
│   │   ├── data-pipeline.md
│   │   ├── local-rag-system.md
│   │   ├── multi-storage-experiment.md
│   │   └── polyglot-lab.md
│   └── router/
│       ├── load-order.md
│       ├── task-routing.md
│       ├── example-priority.md
│       └── stop-conditions.md
├── manifests/
│   ├── repo.profile.yaml
│   ├── archetype.prompt-first.yaml
│   ├── archetype.backend-api.yaml
│   ├── stack.python-fastapi-polars-htmx-plotly.yaml
│   ├── stack.typescript-hono-bun-drizzle-tsx.yaml
│   ├── workflow.add-api-endpoint.yaml
│   ├── workflow.add-smoke-tests.yaml
│   └── infra.compose-dokku.yaml
├── examples/
│   └── canonical/
│       ├── README.md
│       ├── prompt-first/
│       ├── api-endpoints/
│       ├── htmx-plotly/
│       ├── smoke-tests/
│       └── docker-compose/
├── templates/
│   └── base/
│       ├── README.md
│       └── repo.profile.template.yaml
├── scripts/
│   ├── README.md
│   └── validate_context_layout.py
└── smoke-tests/
    └── README.md
```

## SECTION 4 - File semantics contract

### `context/doctrine`

- Belongs: durable principles, invariants, repo preferences
- Does not belong: task checklists, stack-specific code details, long examples
- Naming: numbered files for stable load order
- Size: 40-120 lines per file
- Load when: the task touches the rule governed by the doctrine
- Scope: global

### `context/skills`

- Belongs: reusable specialty packs when a task requires a narrow competency
- Does not belong: repo-wide doctrine or one-off task notes
- Naming: verb-capability or domain-capability
- Size: 1 focused file plus optional assets
- Load when: task wording clearly calls for the capability
- Scope: reusable specialty layer

### `context/workflows`

- Belongs: sequence-oriented task execution guidance
- Does not belong: permanent philosophy or framework reference
- Naming: imperative verb phrase
- Size: 40-100 lines
- Load when: a task matches the workflow intent
- Scope: task-specific

### `context/stacks`

- Belongs: language/framework/storage/deploy conventions
- Does not belong: repo-specific history or ad hoc fixes
- Naming: deterministic stack slug
- Size: 60-150 lines
- Load when: the repo uses the stack or the task touches it
- Scope: stack-specific

### `context/archetypes`

- Belongs: repo-shape expectations and common file layouts
- Does not belong: framework minutiae
- Naming: archetype slug
- Size: 50-120 lines
- Load when: repo profile or task implies the archetype
- Scope: archetype-specific

### `manifests`

- Belongs: load metadata, triggers, compatibility, infra rules
- Does not belong: prose essays
- Naming: `<kind>.<slug>.yaml`
- Size: 20-120 lines
- Load when: always start with repo profile; then task-specific manifests as needed
- Scope: routing metadata

### `examples`

- Belongs: canonical implementation references with metadata
- Does not belong: incomplete experiments or stale scratch code
- Naming: stable pattern-oriented folders
- Size: 1 small self-contained example per pattern
- Load when: after doctrine/workflow/archetype/stack selection
- Scope: reference material

### `templates`

- Belongs: bootstrap starters for new repos or new modules
- Does not belong: finished canonical examples
- Naming: `*.template.*` or starter-file names inside template folders
- Size: concise bootstrap artifacts
- Load when: bootstrapping, not during normal feature work
- Scope: scaffolding

### `docs`

- Belongs: operator manuals, architecture rationale, checklists
- Does not belong: canonical examples or machine-routing metadata
- Naming: descriptive nouns
- Size: long-form okay
- Load when: first-time orientation or when a router points there
- Scope: human reference

### `scripts`

- Belongs: validation, bundling, bootstrap helpers
- Does not belong: repo business logic from downstream projects
- Naming: action-oriented snake_case
- Size: small utilities
- Load when: executing validation or automation, not as default reading
- Scope: tooling

### `smoke-tests` or `tests`

- Belongs: operational smoke tests and minimal real-infra integration contracts
- Does not belong: doctrine docs
- Naming: scenario-first
- Size: scenario-sized
- Load when: task affects runtime behavior, infra, persistence, queues, search, or deployment
- Scope: verification

### Repo-level infrastructure conventions

Keep infra rules in two places:

- durable doctrine: `context/doctrine/04-compose-port-isolation.md`
- routing metadata: `manifests/infra.compose-dokku.yaml`

Required rules:

- Compose files stay named `docker-compose.yml` and `docker-compose.test.yml`
- top-level Compose `name:` is repo-derived
- primary/dev stack uses `<repo-slug>`
- test stack uses `<repo-slug>-test`
- host ports are explicit non-default values
- test ports use a separate non-default band
- test env files, volumes, databases, fixtures, and seeds are isolated from dev-like data

## SECTION 5 - Agent routing rules

### Shared strategy for `AGENT.md` and `CLAUDE.md`

Shared:

- first reads
- smallest-bundle-first rule
- example-first bias
- stop conditions
- anti-hallucination guardrails

Different:

- `AGENT.md` can be more imperative and brief
- `CLAUDE.md` can afford slightly more explanation but should still route rather than dump

### Top-level versus delegated content

Top-level files should contain:

- purpose
- first reads
- load order
- stop conditions
- links to delegated packs

Delegated files should contain:

- doctrine specifics
- task workflows
- stack conventions
- archetype conventions
- example priority policy

### Encoding load order

Use explicit numbered lists in top-level files and metadata in manifests:

1. repo profile
2. router files
3. doctrine subset
4. workflow
5. archetype pack
6. stack pack subset
7. examples

### Encoding "do not load unless needed"

State exclusion rules directly in routers and manifests:

- unrelated stacks are excluded by default
- retired examples are excluded unless no active example exists
- deployment docs stay unloaded during local-only changes

### Prioritizing canonical examples

- examples carry metadata in folder README or manifest
- one preferred example per pattern family
- conflicting alternates are marked as secondary or retired

### Stop conditions and anti-hallucination guardrails

- stop when stack or archetype inference conflicts
- stop when no preferred example exists for a sensitive change
- stop when infra or persistence is touched without smoke/integration coverage
- do not invent file paths or port rules without manifest support

The sample `AGENT.md` and `CLAUDE.md` are the committed top-level files in this repo.

## SECTION 6 - Task-to-context mapping

| Task type | Doctrine to load | Workflow to load | Stack packs | Archetype packs | Canonical examples | Do not load initially |
| --- | --- | --- | --- | --- | --- | --- |
| add API endpoint | `02-testing-philosophy`, `09-context-loading-rules` | `add-api-endpoint` | active backend stack, `docker-compose-dokku` if infra-backed | `backend-api` | `examples/canonical/api-endpoints/` | unrelated storage packs |
| extend CLI command | `01-naming-and-clarity`, `02-testing-philosophy` | `extend-cli` | language stack only | `cli-tool` | future `examples/canonical/cli/` | HTMX or deploy docs |
| add HTMX fragment workflow | `01-naming-and-clarity`, `08-canonical-example-policy` | `add-feature` | active web stack | `backend-api` or `interactive` derivative | `examples/canonical/htmx-plotly/` | queue/search packs |
| add Plotly chart | `06-documentation-philosophy`, `08-canonical-example-policy` | `add-feature` | active web stack, maybe `trino-duckdb-polars` | `backend-api` or data app | `examples/canonical/htmx-plotly/` | unrelated CLI docs |
| add seed data generator | `04-compose-port-isolation`, `02-testing-philosophy` | `add-seed-data` | active backend stack, relevant storage pack | active archetype | `examples/canonical/docker-compose/` | unrelated prompt docs |
| add smoke tests | `03-smoke-test-philosophy`, `04-compose-port-isolation` | `add-smoke-tests` | active stack, `docker-compose-dokku` if needed | active archetype | `examples/canonical/smoke-tests/` | unrelated alternative stacks |
| bootstrap new prompt-first repo | `07-prompt-first-conventions`, `09-context-loading-rules` | `bootstrap-repo` | prompt support, optional stack pack | `prompt-first-repo` | `examples/canonical/prompt-first/` | storage/search packs |
| generate new prompt sequence | `07-prompt-first-conventions` | `generate-prompt-sequence` | none unless runtime involved | `prompt-first-repo` | `examples/canonical/prompt-first/` | backend stacks |
| refactor Docker Compose stack | `04-compose-port-isolation`, `10-deployment-dokku-thinking` | `refactor` or `add-deployment-support` | `docker-compose-dokku`, relevant storage packs | active archetype | `examples/canonical/docker-compose/` | unrelated app frameworks |
| add local RAG indexing step | `02-testing-philosophy`, `09-context-loading-rules` | `add-local-rag-indexing` | `python-fastapi...` or relevant runtime, `timescaledb-elasticsearch-qdrant` if used | `local-rag-system` | future `examples/canonical/local-rag/` | unrelated web stacks |
| add Redis-backed workflow | `04-compose-port-isolation`, `02-testing-philosophy` | `add-storage-integration` | `redis-mongodb`, active app stack | `backend-api` or `event-driven` derivative | future `examples/canonical/storage/redis/` | prompt-only docs |
| add MongoDB aggregation workflow | `02-testing-philosophy`, `04-compose-port-isolation` | `add-storage-integration` | `redis-mongodb` | `backend-api`, `multi-storage-experiment` | future `examples/canonical/storage/mongodb/` | queue/search packs |
| add Trino catalog experiment | `09-context-loading-rules`, `04-compose-port-isolation` | `add-storage-integration` | `trino-duckdb-polars` | `multi-storage-experiment` | future `examples/canonical/storage/trino/` | Phoenix or HTMX docs |
| add NATS Jetstream workflow | `02-testing-philosophy`, `04-compose-port-isolation` | `add-storage-integration` | `nats-jetstream-meilisearch` | `backend-api` or event-driven derivative | future `examples/canonical/messaging/` | prompt-first docs |
| add Meilisearch workflow | `02-testing-philosophy`, `08-canonical-example-policy` | `add-storage-integration` | `nats-jetstream-meilisearch` | `backend-api` | future `examples/canonical/search/` | unrelated database packs |
| add TimescaleDB workflow | `02-testing-philosophy`, `04-compose-port-isolation` | `add-storage-integration` | `timescaledb-elasticsearch-qdrant` | `backend-api` or analytics app | future `examples/canonical/storage/timescaledb/` | unrelated prompt docs |
| add Qdrant workflow | `02-testing-philosophy`, `04-compose-port-isolation` | `add-storage-integration` | `timescaledb-elasticsearch-qdrant` | `local-rag-system` or `backend-api` | future `examples/canonical/storage/qdrant/` | unrelated queue packs |
| add TypeScript Hono service route | `01-naming-and-clarity`, `02-testing-philosophy` | `add-api-endpoint` | `typescript-hono-bun-drizzle-tsx` | `backend-api` | `examples/canonical/api-endpoints/ts-hono/` | Rust/Go/Python stack docs |
| add Rust Axum service route | `01-naming-and-clarity`, `02-testing-philosophy` | `add-api-endpoint` | `rust-axum` | `backend-api` | `examples/canonical/api-endpoints/rust-axum/` | other backend stacks |
| add Go Echo templ middleware or handler flow | `01-naming-and-clarity`, `08-canonical-example-policy` | `add-feature` or `add-api-endpoint` | `go-echo-templ` | `backend-api` | `examples/canonical/api-endpoints/go-echo/` | unrelated stacks |
| add Elixir Phoenix middleware | `01-naming-and-clarity`, `02-testing-philosophy` | `add-feature` | `elixir-phoenix` | `backend-api` | future `examples/canonical/api-endpoints/elixir-phoenix/` | non-Elixir stacks |
| stage-2 post-flight refinement | `05-commit-hygiene`, `07-prompt-first-conventions`, `09-context-loading-rules` | `post-flight-refinement` | active stack only if code changes | `prompt-first-repo` or active repo archetype | `examples/canonical/prompt-first/` | unrelated bootstrap templates |

## SECTION 7 - Archetype packs

### Prompt-first repo

- Purpose: ordered prompt files, operator guidance, staged refinement
- Required doctrine: `07-prompt-first-conventions`, `09-context-loading-rules`, `05-commit-hygiene`
- Required workflows: `bootstrap-repo`, `generate-prompt-sequence`, `post-flight-refinement`
- Common stacks: none mandatory; may pair with any backend stack
- Canonical examples: monotonic prompt numbering, meta-runner patterns, output-target declaration
- Likely scripts or smoke tests: prompt lint, prompt sequence validator
- Warnings: never break numbering monotonicity; never hide output targets

### Backend API

- Purpose: HTTP service repos with persistence/integration surfaces
- Required doctrine: testing, smoke, compose isolation
- Required workflows: add endpoint, add feature, add smoke tests, add storage integration
- Common stacks: FastAPI, Hono, Echo, Axum, Phoenix
- Canonical examples: route handler, middleware, smoke test, integration test
- Likely scripts: health checks, seed/reset helpers
- Warnings: mock-only coverage for persistence is insufficient

### CLI tool

- Purpose: command-line programs with deterministic IO contracts
- Required doctrine: naming, testing, docs philosophy
- Required workflows: extend CLI, fix bug, refactor
- Common stacks: Python, Rust, Go, Bun
- Canonical examples: command registration, config loading, error output
- Likely scripts: smoke scripts for command success/failure
- Warnings: avoid burying side effects in argument parsing

### Data pipeline

- Purpose: extract-transform-load or analysis pipelines
- Required doctrine: testing, data isolation, documentation
- Required workflows: add feature, add seed data, add storage integration
- Common stacks: Python/Polars, DuckDB, Trino
- Canonical examples: batch step, schema contract, fixture dataset
- Likely scripts: pipeline smoke run, schema validation
- Warnings: dev/test data paths must be distinct

### Local RAG system

- Purpose: local indexing, retrieval, metadata extraction, minimal UI/API
- Required doctrine: testing, compose isolation, canonical examples
- Required workflows: add local RAG indexing, add feature, add smoke tests
- Common stacks: Python plus Qdrant/Elasticsearch/Meilisearch
- Canonical examples: chunking step, metadata extraction, query route
- Likely scripts: indexing smoke, retrieval smoke
- Warnings: do not treat embeddings/index data as shared across dev and test

### Multi-storage experiment

- Purpose: compare databases, search engines, queues, or analytics systems
- Required doctrine: context loading, compose isolation, documentation
- Required workflows: add storage integration, refactor, add smoke tests
- Common stacks: Trino, DuckDB, MongoDB, Redis, NATS, Meilisearch, TimescaleDB, Elasticsearch, Qdrant
- Canonical examples: side-by-side compose stack, catalog config, comparison harness
- Likely scripts: matrix smoke tests
- Warnings: avoid turning experiments into undocumented production defaults

### Polyglot lab

- Purpose: one repo family exploring several language/runtime options
- Required doctrine: naming, context loading, canonical examples
- Required workflows: bootstrap repo, add feature, refactor
- Common stacks: all primary and extension backends
- Canonical examples: equivalent route and smoke patterns across stacks
- Likely scripts: cross-stack smoke suites
- Warnings: keep per-stack conventions separate; never blend code patterns

## SECTION 8 - Stack packs

### Python FastAPI Polars HTMX Plotly

- Overview: API and interactive data app stack with `uv`, `ruff`, `orjson`, and Polars-heavy data paths
- Coding conventions: thin route layer, typed service functions, explicit schema boundaries, Polars for table logic
- Common paths: `app/`, `app/routes/`, `app/services/`, `app/templates/`, `tests/`
- Typical change surfaces: route handlers, HTMX partials, Plotly serialization, seed scripts
- Testing expectations: unit plus smoke; real Docker-backed tests when persistence or external services are involved
- Infra expectations: compose names from repo slug; non-default host ports; separate test env and volumes
- Canonical example wish list: route + service + smoke test + HTMX fragment + Plotly endpoint
- Risks: bloated route files, pandas drift, mock-only DB coverage

### TypeScript Hono Bun Drizzle TSX

- Overview: lightweight backend and HTMX-serving stack
- Coding conventions: route modules stay small, service layer explicit, Drizzle schema authoritative
- Common paths: `src/routes/`, `src/services/`, `src/db/`, `src/views/`, `tests/`
- Typical change surfaces: Hono route modules, TSX view fragments, Drizzle migrations
- Testing expectations: route smoke tests and real infra tests for DB/search/queue interactions
- Infra expectations: explicit port bands for dev and test; isolated DB and env files
- Canonical examples: Hono route, TSX fragment, Drizzle-backed smoke test
- Risks: route files turning into controllers plus service logic plus SQL

### Go Echo templ

- Overview: server-rendered HTMX-friendly service with strong compile-time templates
- Coding conventions: handlers thin, templ components composable, services explicit
- Common paths: `cmd/`, `internal/http/`, `internal/services/`, `internal/views/`, `tests/`
- Typical change surfaces: Echo middleware, templ components, service wiring
- Testing expectations: handler smoke tests and infra-backed tests for storage or queue changes
- Infra expectations: same Compose and port isolation rules
- Canonical examples: middleware + handler + templ fragment + smoke test
- Risks: business logic inside handlers, duplicate DTO shapes

### Rust Axum

- Overview: strongly typed API service stack
- Coding conventions: extractor-driven handlers, explicit state wiring, crates kept coherent
- Common paths: `src/routes/`, `src/state/`, `src/services/`, `tests/`
- Typical change surfaces: route registration, state/config, integration tests
- Testing expectations: cargo unit tests plus infra-backed integration tests when boundaries matter
- Infra expectations: same compose naming and isolation rules
- Canonical examples: Axum route + shared state + integration test
- Risks: over-generic abstractions and async error-type sprawl

### Additional backend candidates

- Nim `Jester` `HappyX`: keep routing simple, prefer one clear service layer
- Zig `Zap` `Jetzig`: prioritize explicit HTTP flow and minimal magic
- Scala `Tapir` `http4s` `ZIO`: use typed endpoints and effect boundaries carefully
- Clojure `Kit` `next.jdbc` `Hiccup`: keep data shape docs explicit
- Kotlin `http4k` `Exposed`: prefer functional routing and thin transaction boundaries
- Crystal `Kemal` `Avram`: keep ORM and HTTP concerns separate
- OCaml `Dream` `Caqti` `TyXML`: use module boundaries to reduce cognitive load
- Dart `Dart Frog`: keep route folder conventions explicit

Each extension stack pack should define:

- expected folders
- route and handler conventions
- smoke-test expectations
- one canonical example per common change surface

### Docker Compose Dokku

- Overview: local orchestration plus simple deploy packaging
- Conventions: keep filenames conventional, set top-level `name:` from repo slug
- Dev/test isolation: primary `<repo>`, test `<repo>-test`
- Port strategy: non-default explicit host ports; test band distinct from primary
- Risks: accidental shared volumes, default ports, implicit project names

### Redis MongoDB

- Overview: cache/document-store pair for workflow state and aggregation experiments
- Conventions: treat each service as an explicit dependency with smoke coverage
- Change surfaces: connection config, data access layer, seed/reset scripts
- Testing expectations: real infra tests for pipelines, TTL behavior, aggregation logic
- Risks: hidden shared state, brittle fixtures

### Trino DuckDB Polars

- Overview: analytics and exploration stack
- Conventions: DuckDB local fast path, Trino cataloged comparison path, Polars in process
- Change surfaces: query modules, catalog config, local dataset scripts
- Testing expectations: query smoke tests with known fixtures
- Risks: inconsistent schema assumptions across engines

### NATS Jetstream Meilisearch

- Overview: eventing plus lightweight search
- Conventions: explicit subject naming, idempotent consumers, index refresh clarity
- Change surfaces: publisher/consumer contracts, indexing steps, search queries
- Testing expectations: real infra tests for publish-consume-index flow
- Risks: silently async failures, stale index assumptions

### TimescaleDB Elasticsearch

- Overview: time-series analytics plus full-text/search analytics
- Conventions: keep schema/mapping artifacts versioned and testable
- Change surfaces: migrations, index mappings, query adapters
- Testing expectations: real infra tests for inserts, refresh, retrieval
- Risks: drift between SQL and search representations

## SECTION 9 - Canonical examples strategy

Choose examples that are:

- small enough to load quickly
- complete enough to copy safely
- representative of the preferred local pattern
- tested or smoke-validated

Keep:

- one preferred example per pattern family
- at most two alternates when genuinely needed
- retired examples in a clearly marked `retired/` subtree or removed entirely

Mark preferred examples with metadata in their local README or manifest.

Retirement rules:

- retire when stack version, doctrine, or preferred architecture changes materially
- replace with a new preferred example in the same pattern family
- note the reason for retirement

Avoid example blending by:

- grouping examples by pattern family
- marking one preferred implementation
- explicitly noting incompatible alternates

Recommended layout:

```text
examples/canonical/
├── README.md
├── prompt-first/
│   ├── monotonic-sequence/
│   └── post-flight-stage2/
├── api-endpoints/
│   ├── python-fastapi/
│   ├── ts-hono/
│   ├── go-echo/
│   └── rust-axum/
├── htmx-plotly/
├── smoke-tests/
├── docker-compose/
└── retired/
```

## SECTION 10 - Manifest/profile loading system

### Schema design

Use YAML with predictable fields:

```yaml
kind: repo_profile | archetype | stack | workflow | infra
slug: string
summary: string
load_order: integer
required_files:
  - path
optional_files:
  - path
trigger_keywords:
  - string
compatibility:
  archetypes: [slug]
  stacks: [slug]
infra:
  compose:
    dev_file: docker-compose.yml
    test_file: docker-compose.test.yml
    dev_name: <repo-slug>
    test_name: <repo-slug>-test
  ports:
    dev_band: "18xxx"
    test_band: "28xxx"
  isolation:
    separate_env_files: true
    separate_volumes: true
    separate_seed_flows: true
```

### Load order semantics

- lower `load_order` means earlier read
- `repo_profile` is always first
- workflows are loaded after doctrine and before examples
- examples are optional unless a task touches a known pattern family

### Optional versus required context

- `required_files`: must be read before action
- `optional_files`: load only if task scope expands

### Trigger keywords

Use user-facing natural language, not internal jargon. The human should not need to memorize manifest names.

### Compatibility metadata

Each manifest lists compatible archetypes and stacks so routers can avoid invalid combinations.

### Infrastructure metadata

Put Compose filenames, repo-derived `name:` values, host-port bands, and dev/test isolation rules in the repo profile and infra manifest.

### Future automation notes

- scripts can validate manifest schema
- scripts can produce a context bundle preview
- bootstrap tools can select template sets from manifests

The eight example manifests are committed under `manifests/`.

## SECTION 11 - Example implementations for real workflows

### 1. Prompt-first repo for a polyglot backend lab

- Create: `.prompts/`, `context/`, `manifests/repo.profile.yaml`, `examples/canonical/prompt-first/`
- Archetypes: `prompt-first-repo`, `polyglot-lab`
- Mandatory first reads: `AGENT.md`, repo profile, prompt-first doctrine
- Most important examples: monotonic prompt sequence, post-flight refinement
- Isolation: if services exist, dev and test compose stacks use distinct names and port bands

### 2. Python FastAPI Polars service with smoke tests and seed data

- Create: `app/`, `tests/`, `docker-compose.yml`, `docker-compose.test.yml`, seed scripts
- Archetype: `backend-api`
- Stacks: `python-fastapi-polars-htmx-plotly`, `docker-compose-dokku`
- Mandatory first reads: testing doctrine, compose isolation doctrine, add endpoint workflow
- Examples: Python endpoint, smoke test, docker compose example
- Isolation: `repo-slug` and `repo-slug-test`, separate DB volumes and `.env.test`

### 3. FastAPI HTMX Plotly dashboard with Docker-backed local services

- Create: template/view folders, fragment routes, Plotly data endpoints, smoke tests
- Archetype: backend API plus interactive data app variant
- Stacks: Python stack, Redis/Mongo or analytics pack as needed
- Mandatory first reads: canonical example policy, stack pack, smoke-test workflow
- Examples: HTMX fragment and Plotly example set
- Isolation: separate dev/test ports for web, Redis, and DB services

### 4. TypeScript Hono Bun Drizzle TSX service with HTMX fragments and smoke tests

- Create: `src/routes/`, `src/views/`, `src/db/`, `tests/`, compose files
- Archetype: `backend-api`
- Stacks: TS Hono/Bun/Drizzle, Docker Compose
- Mandatory first reads: naming doctrine, add endpoint workflow, smoke-test workflow
- Examples: TS Hono route and TSX fragment
- Isolation: distinct Bun app ports and DB ports in dev/test bands

### 5. Go Echo templ backend service with canonical middleware and smoke tests

- Create: `cmd/`, `internal/http/`, `internal/views/`, `tests/`
- Archetype: `backend-api`
- Stacks: Go Echo templ, Docker Compose
- Mandatory first reads: Go stack pack, add feature workflow
- Examples: middleware and templ example
- Isolation: separate test compose file and volumes

### 6. Rust Axum API with route patterns and integration tests

- Create: `src/routes/`, `src/services/`, `tests/integration/`, compose files if persistence exists
- Archetype: `backend-api`
- Stacks: Rust Axum, optional storage packs
- Mandatory first reads: Rust stack pack, testing doctrine
- Examples: Axum route and infra-backed integration example
- Isolation: separate DB and message-bus test instances

### 7. Nim or Zig backend sketch for experimental server rendering

- Create: one service folder, one smoke test, one example route
- Archetype: `polyglot-lab`
- Stacks: backend extension candidate plus Docker Compose if needed
- Mandatory first reads: backend-extension pack, canonical-example policy
- Examples: parallel endpoint pattern from a primary stack
- Isolation: keep experimental service on its own non-default port band

### 8. Local RAG repo with indexing, metadata extraction, and minimal web UI

- Create: indexer module, retrieval API/UI, local vector/search services, smoke tests
- Archetype: `local-rag-system`
- Stacks: Python or TS plus `timescaledb-elasticsearch-qdrant` as needed
- Mandatory first reads: local RAG workflow, compose isolation doctrine
- Examples: indexing and retrieval canonical examples
- Isolation: separate dev/test indexes, collections, and data dirs

### 9. Multi-storage zoo repo with Trino and Docker Compose

- Create: `docker-compose.yml`, `docker-compose.test.yml`, per-store configs, comparison scripts
- Archetype: `multi-storage-experiment`
- Stacks: `trino-duckdb-polars`, `redis-mongodb`, `timescaledb-elasticsearch-qdrant`
- Mandatory first reads: compose isolation doctrine, add storage integration workflow
- Examples: docker compose and storage comparison examples
- Isolation: every store gets separate dev/test env files and volumes

### 10. Prompt meta-runner repo with post-flight and stage-2 prompts

- Create: `.prompts/`, meta-runner docs, validation scripts, stage-2 workflow notes
- Archetype: `prompt-first-repo`
- Stacks: prompt-first support only unless runtime helpers are added
- Mandatory first reads: prompt-first doctrine, generate prompt sequence workflow, post-flight workflow
- Examples: prompt-first canonical examples
- Isolation: if helper services exist, same parallel dev/test rules apply

## SECTION 12 - Cross-model guidance

### Codex

- Best with terse routers and explicit file paths
- Responds well to manifests and canonical examples
- Failure pattern: moving too fast with partial inference
- Mitigation: strong stop conditions and ordered first reads

### Claude

- Tolerates more prose but may over-read if given permission
- Benefits from delegated files and explicit "do not load unless needed" rules
- Failure pattern: synthesizing elegant but non-canonical structures
- Mitigation: example-first priority and compatibility metadata

### Gemini

- Benefits from explicit metadata and deterministic manifests
- Failure pattern: broader inference from partial repo signals
- Mitigation: make routing files and manifest compatibility very explicit

One shared system serves all three if:

- the top-level routers stay small
- manifests stay current
- canonical examples are clearly preferred
- doctrine is separated from workflows and stacks

## SECTION 13 - Anti-patterns and quality rubric

### Likely mistakes

- giant top-level instruction files
- doctrine mixed with examples
- multiple conflicting canonical examples with no preferred marker
- stack packs that encode repo-specific hacks
- templates used as live examples
- implicit Compose project names
- default host ports
- shared dev/test volumes or seed flows
- mock-only testing for persistence-heavy changes
- no manifest ownership or refresh discipline

### Quality rubric

Score each category from 1 to 5.

| Category | 1 | 3 | 5 |
| --- | --- | --- | --- |
| clarity | vague and overlapping | mostly clear | deterministic and easy to navigate |
| modularity | giant docs | some layering | clean doctrine/workflow/stack/archetype separation |
| minimal-load design | frequent bulk loading | partial routing | smallest-bundle-first works reliably |
| example quality | stale or absent | mixed quality | preferred canonical examples are current and trusted |
| routing quality | ad hoc | partly manifest-driven | deterministic across common tasks |
| archetype reuse | one-off repo design | some reuse | archetype packs are portable and composable |
| stack specificity | generic advice | partial conventions | concrete paths, risks, and test expectations |
| anti-drift protection | none | manual discipline only | manifests, examples, and routers are validated |
| frontier-model friendliness | optimized for one model | usable by several | explicitly balanced for Codex, Claude, Gemini |
| long-term maintainability | brittle and duplicated | acceptable | small files, clear owners, easy retirement paths |

## SECTION 14 - Deliverables

### Initial implementation pass

- top-level routers
- architecture spec
- doctrine core
- workflow core
- primary stack packs
- primary archetype packs
- repo profile and infra manifests
- first canonical-example folders
- layout validation script

### Phase 2 expansion pass

- richer example inventory
- archetype bootstrap generator
- manifest schema validation
- stale example detection
- bundle preview tooling
- AGENT/CLAUDE consistency checks
- automated task-to-context recommender

## SECTION 15 - Optional automation ideas

- manifest validation script against required keys
- stale example detector based on stack version or retired markers
- `AGENT.md` and `CLAUDE.md` consistency checker
- task-to-context recommendation CLI
- context bundle preview generator
- archetype bootstrap generator
- canonical example linting for preferred/secondary/retired state
- Compose name and host-port band validator
- test-data isolation validator for env files, volumes, and seed scripts

## End-state summary

1. Recommended final architecture: Hybrid Layered Router with manifests and canonical examples.
2. Sample `AGENT.md`: committed at repo root.
3. Sample `CLAUDE.md`: committed at repo root.
4. Eight example manifests: committed under `manifests/`.
5. Twenty-row task-to-context mapping table: in Section 6.
6. Prioritized implementation plan: in Section 14.
