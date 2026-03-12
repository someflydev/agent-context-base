# Agent-Oriented Base Repo Architecture

This document is the implementation-oriented architectural brief for `agent-context-base`. It refines `.prompts/PROMPT_00_s.txt` into a reusable base repo contract for future projects.

## SECTION 1 - Purpose and philosophy of the base repo

### What this base repo is

This repo is a reusable foundation for future software projects that will be used with Codex, Claude, and Gemini. It is optimized for:

- prompt-first repo workflows
- deterministic task routing
- doctrine separated from workflows, stacks, archetypes, examples, manifests, and templates
- strong canonical examples
- smoke-test-heavy development
- minimal real-infra integration tests for significant features
- Docker-backed local development with strict dev/test isolation
- Dokku-oriented deployment conventions for small services

### What this base repo is not

- It is not a product monorepo.
- It is not a dumping ground for every pattern from every future repo.
- It is not a substitute for project-specific manifests and examples in derived repos.
- It is not a giant `AGENT.md` or `CLAUDE.md` with all instructions flattened into one file.

### Why it should exist

- Starting from a clean base repo is faster than repeatedly rebuilding routing, doctrine, manifests, examples, templates, and bootstrap scripts.
- Frontier assistants behave better when the repo already encodes task routing and preferred patterns.
- Stable architecture docs reduce operator memory burden and lower onboarding friction.

### Why it should not become a forever-monorepo

- Actual products need their own manifests, examples, scripts, and constraints.
- A giant shared repo would accumulate conflicting patterns across domains and stacks.
- Context quality falls when assistants see too many irrelevant sibling systems.

### Why assistant-oriented context architecture matters

- Frontier assistants perform better with scoped deterministic context than with giant instruction dumps.
- Separate layers let assistants load stable doctrine without also loading unrelated implementation detail.
- Routing files and manifests let the assistant infer what to read from normal English requests.

### Why layers must stay separate

| Layer | Why it exists |
| --- | --- |
| doctrine | durable rules, philosophy, invariants |
| workflows | task sequences |
| stacks | framework and infrastructure specifics |
| archetypes | repo-shape expectations |
| router files | inference and loading rules |
| manifests | machine-readable bundle hints |
| examples | preferred concrete implementations |
| templates | minimal starter scaffolds |

### Why task inference matters more than internal naming

The human should be able to say "add a Redis cache to the Hono service" or "package this FastAPI app for Dokku" and have the assistant infer the right workflow, stack pack, archetype pack, and examples. The operator should not need to remember `add-storage-integration` or `docker-compose-dokku`.

### Why minimal relevant context is the optimization target

- It reduces hallucinated blending across stacks.
- It lowers routing latency and operator burden.
- It keeps doctrine durable and examples trustworthy.
- It makes the same repo architecture work across Codex, Claude, and Gemini.

## SECTION 2 - Recommended final repository architecture

Recommended long-term tree:

```text
.
├── AGENT.md
├── CLAUDE.md
├── README.md
├── .prompts/
│   ├── PROMPT_00_s.txt
│   └── sequences/
├── docs/
│   ├── agent-context-architecture.md
│   ├── operator-manual.md
│   ├── repo-bootstrap-checklist.md
│   └── rubric.md
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
│   │   ├── 10-deployment-dokku-thinking.md
│   │   └── 11-single-service-bias.md
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
│   │   ├── rust-axum.md
│   │   ├── go-echo-templ.md
│   │   ├── elixir-phoenix.md
│   │   ├── backend-extension-candidates.md
│   │   ├── redis-mongodb.md
│   │   ├── trino-duckdb-polars.md
│   │   ├── nats-jetstream-meilisearch.md
│   │   ├── timescaledb-elasticsearch-qdrant.md
│   │   └── docker-compose-dokku.md
│   ├── archetypes/
│   │   ├── prompt-first-repo.md
│   │   ├── backend-api.md
│   │   ├── cli-tool.md
│   │   ├── data-pipeline.md
│   │   ├── local-rag-system.md
│   │   ├── multi-storage-experiment.md
│   │   ├── polyglot-lab.md
│   │   └── dokku-deployable-web-service.md
│   └── router/
│       ├── load-order.md
│       ├── task-router.md
│       ├── stack-router.md
│       ├── archetype-router.md
│       ├── alias-catalog.md
│       ├── example-priority.md
│       └── stop-conditions.md
├── manifests/
│   ├── README.md
│   ├── repo.profile.yaml
│   ├── schema.profile.example.yaml
│   └── profiles/
│       ├── backend-api-fastapi-polars.yaml
│       ├── backend-api-typescript-hono-bun.yaml
│       ├── backend-api-rust-axum.yaml
│       ├── backend-api-go-echo.yaml
│       ├── webapp-elixir-phoenix.yaml
│       ├── prompt-first-meta-repo.yaml
│       ├── local-rag-base.yaml
│       ├── multi-storage-zoo.yaml
│       ├── cli-python.yaml
│       ├── data-pipeline-polars.yaml
│       ├── dokku-deployable-fastapi.yaml
│       ├── dokku-deployable-typescript-hono-bun.yaml
│       ├── dokku-deployable-go-echo.yaml
│       └── dokku-deployable-phoenix.yaml
├── examples/
│   ├── canonical/
│   │   ├── README.md
│   │   ├── api-endpoints/
│   │   ├── smoke-tests/
│   │   ├── docker-compose/
│   │   ├── dokku-deployment/
│   │   ├── cli/
│   │   ├── prompt-first/
│   │   ├── seed-data/
│   │   ├── storage-integration/
│   │   └── local-rag/
│   └── retired/
├── templates/
│   ├── base/
│   ├── manifests/
│   ├── prompt-first/
│   ├── fastapi/
│   ├── hono-bun/
│   ├── rust-axum/
│   ├── go-echo/
│   ├── phoenix/
│   ├── dokku/
│   ├── smoke-tests/
│   └── seed-data/
├── scripts/
│   ├── README.md
│   ├── validate_context_layout.py
│   ├── validate_manifests.py
│   ├── validate_router_refs.py
│   ├── detect_stale_examples.py
│   ├── preview_context_bundle.py
│   ├── build_repo_from_profile.py
│   ├── generate_agent_files.py
│   ├── lint_alias_collisions.py
│   └── check_internal_links.py
├── smoke-tests/
│   ├── README.md
│   ├── api/
│   ├── cli/
│   ├── pipeline/
│   ├── rag/
│   └── deploy/
└── tests/
    └── integration/
```

## SECTION 3 - Directory semantics contract

| Path | What belongs there | What does not belong there | Naming | Ideal scope | Type | Load when | Avoid when |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AGENT.md` | Codex router | doctrine dumps, full stack docs | fixed | 80-180 lines | router | Codex is active | never as sole source of truth |
| `CLAUDE.md` | Claude router | giant all-repo narrative | fixed | 80-180 lines | router | Claude is active | never bulk-loaded for code-only task if another router already loaded |
| `README.md` | repo purpose and entrypoints | task details, stack internals | fixed | 40-120 lines | global | always first | never substitute for manifests |
| `docs/` | human-oriented architecture and operator docs | code examples that should be canonical examples | kebab-case | 1 concept per file | durable reference | during design, bootstrap, maintenance | for small code edits once routing is settled |
| `context/doctrine/` | durable rules and preferences | task steps, templates, code snippets | numeric prefix + kebab-case | 1 durable principle | doctrine | whenever task touches that rule | when irrelevant to current task |
| `context/skills/` | narrow reusable capability packs | broad architecture doctrine | kebab-case | specialized and compact | skill | only when named or clearly matched | for normal routing if a workflow already covers it |
| `context/workflows/` | task sequences | framework specifics | kebab-case verb phrase | 1 task | task-specific | once task is known | when task is unrelated |
| `context/stacks/` | stack-specific conventions | generic doctrine | stack name | 1 stack or paired infra family | stack-specific | once stack is known | never load sibling stacks by default |
| `context/archetypes/` | repo-shape expectations | stack-specific details | archetype name | 1 archetype | archetype-specific | once repo shape is known | for unrelated repo shapes |
| `context/router/` | load order, heuristics, stop rules, aliases | stack details, templates | fixed names | short deterministic docs | router | near the start | not all at once if not needed |
| `manifests/` | machine-readable bundle hints | prose-heavy docs | kebab-case | 1 profile per file | routing metadata | always profile first, examples later | not a substitute for code truth |
| `examples/canonical/` | preferred concrete patterns | scaffolds meant for generation | category folders | 1 preferred example per pattern family | canonical reference | before inventing a new pattern | when unrelated to change surface |
| `templates/` | minimal composable starters | productionized examples | category folders | smallest scaffold that composes | bootstrap material | only during bootstrap/scaffold | for routine edits |
| `scripts/` | validation, bundle preview, bootstrap helpers | app logic | snake_case | 1 script = 1 job | automation | during maintenance/bootstrap | when a shell one-liner is enough |
| `smoke-tests/` | reusable smoke starter assets and conventions | full integration suites | category folders | smallest runnable checks | testing starter | when adding verification | for logic-only refactors |
| `tests/integration/` | minimal real-infra integration tests | unit tests and smoke starter docs | stack/test naming | few happy-path tests with a few edge cases | repo tests | when feature touches infra boundary | for pure docs/prompts changes |

### Specific distinctions

| Layer | Definition | Example |
| --- | --- | --- |
| doctrine | durable preferences and invariants | `04-compose-port-isolation.md` |
| skills | narrow reusable knowledge packs | `canonical-example-curator.md` |
| workflows | how to execute a task | `add-api-endpoint.md` |
| stacks | framework/tooling specifics | `go-echo-templ.md` |
| archetypes | project shape patterns | `local-rag-system.md` |
| router files | inference and bundle selection rules | `task-router.md` |
| manifests | machine-readable load hints | `backend-api-fastapi-polars.yaml` |
| canonical examples | preferred implementation references | `examples/canonical/api-endpoints/` |
| templates | starter scaffolds intended for copying | `templates/fastapi/` |

## SECTION 4 - Top-level routing strategy

### Plain-English task router strategy

1. Parse the user's words first, not internal names.
2. Map verbs to workflows.
3. Map nouns to archetypes and stack packs.
4. Confirm with repo profile and repo signals.
5. Load the smallest bundle that can answer or implement safely.

### Stack inference strategy

1. Repo profile manifest.
2. Tool files and lockfiles.
3. Dominant source tree.
4. Existing canonical examples already referenced locally.
5. Deployment/config signals.

### Archetype inference strategy

1. Repo profile.
2. Directory structure.
3. Operator request wording.
4. Existing tests and examples.

### Canonical examples priority strategy

1. Use the preferred example for the relevant pattern family.
2. Use a secondary example only if the preferred one is stack-incompatible.
3. Retired examples are reference-only and should not drive new work.

### Stop conditions

- stack ambiguous
- archetype ambiguous
- manifest and repo signals conflict
- persistence or service boundary touched without smoke and integration path
- dev/test isolation unclear
- only stale or conflicting example exists

### Anti-hallucination guardrails

- never infer ports without the manifest
- never reuse dev env files or volumes for test
- never invent stack conventions if a stack pack exists
- never blend multiple canonical examples for the same pattern family
- never claim infra isolation if the compose names, ports, volumes, and seeds are not separate

### Escalation logic

Escalate bundle size only when:

- one workflow does not cover the task
- a second archetype materially changes behavior
- a second stack is genuinely part of the target surface
- no canonical example exists

### Load-smallest-bundle-first rules

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `AGENT.md` or `CLAUDE.md`
4. `context/router/task-router.md`
5. doctrine files directly relevant to the task
6. one workflow
7. one archetype pack
8. required stack packs
9. one preferred canonical example
10. templates only for bootstrap

### Model-specific notes

| Model | Guidance |
| --- | --- |
| Codex | optimize for deterministic routing, concrete files, small bundle size |
| Claude | allow slightly more prose, but keep router strict and delegated |
| Gemini | rely on explicit manifests, aliases, and short factual routing docs |

## SECTION 5 - AGENT.md and CLAUDE.md design

### Shared content

- repo purpose
- required first reads
- minimal-bundle rule
- context priority
- stop conditions
- canonical example rule
- router delegate file list

### Differences

- `AGENT.md` should be slightly more procedural and terse.
- `CLAUDE.md` can allow one extra model-specific note about resisting over-reading.
- Neither should duplicate doctrine or stack content.

### Router-not-dump design

- keep both files short
- push real detail into doctrine, workflows, stacks, archetypes, and router docs
- encode first reads and stop conditions directly

### Required first reads

- `README.md`
- `manifests/repo.profile.yaml`
- `context/router/load-order.md`
- `context/router/task-router.md`

### Stack/archetype/task routing references

- `context/router/stack-router.md`
- `context/router/archetype-router.md`
- `context/router/alias-catalog.md`

### Canonical example reference rule

Both router files should say: use preferred canonical examples before inventing new patterns.

### Stop conditions in router files

Both router files should tell the model to stop when:

- stack or archetype is unclear
- manifest disagrees with repo signals
- storage or infra changes lack real verification path

### Draft status

Draft starter versions have been implemented in:

- `AGENT.md`
- `CLAUDE.md`

These should be treated as the v1 router drafts for this base repo.

## SECTION 6 - Doctrine pack design

| Doctrine doc | Purpose | Assistant should learn | Common mistake prevented |
| --- | --- | --- | --- |
| `00-core-principles.md` | define the repo's operating philosophy | small deterministic bundles, clarity, composability | turning the repo into a giant instruction blob |
| `01-naming-and-clarity.md` | naming rules and file clarity | deterministic names, explicitness, low ambiguity | vague names like `helpers2.py` or `service-final.ts` |
| `02-testing-philosophy.md` | overall testing doctrine | unit tests plus smoke tests plus minimal real integration where significant | mock-only confidence |
| `03-smoke-test-philosophy.md` | define smoke-test expectations | startup, health, key flow verification | confusing smoke tests with large integration suites |
| `04-compose-port-isolation.md` | Docker Compose and data isolation invariants | conventional filenames, repo-derived names, non-default ports, test isolation | test touching dev data or port collisions |
| `05-commit-hygiene.md` | commit and diff quality | scoped changes, readable commits, no accidental churn | giant mixed commits |
| `06-documentation-philosophy.md` | docs discipline | concise, composable, referenceable docs | giant stale prose dumps |
| `07-prompt-first-conventions.md` | prompt-first repo patterns | ordered prompts, operator guidance, reusable context docs | mixing prompt strategy into random notes |
| `08-canonical-example-policy.md` | example governance | one preferred example per pattern family | blending conflicting examples |
| `09-context-loading-rules.md` | anti-sprawl rules | load smallest relevant bundle first | loading whole `context/` tree |
| `10-deployment-dokku-thinking.md` | deployment doctrine | prefer simple Dokku path for suitable apps | defaulting to infra-heavy setups |
| `11-single-service-bias.md` | simplicity doctrine | prefer single deployable service when it fits | introducing unnecessary service boundaries |

## SECTION 7 - Workflow pack design

| Workflow doc | Purpose | Expected sequence | Preconditions | Outputs | Common pitfalls | Related doctrine | Related examples |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `add-feature.md` | default feature workflow | infer task, inspect code, implement, verify, update docs | active stack known | feature + tests | over-scoping | `00,02,09` | area-specific example |
| `fix-bug.md` | diagnose and patch regressions | reproduce, narrow cause, patch, verify, add regression test | bug surface known | fix + regression coverage | patching without reproduction | `00,02,03` | smoke or endpoint example |
| `refactor.md` | improve structure safely | define behavior, refactor incrementally, verify | baseline behavior understood | same behavior, cleaner shape | hidden behavior drift | `00,01,02,09` | stack-specific examples |
| `add-smoke-tests.md` | add lightweight verification | identify critical path, add smoke, wire scripts | runnable target exists | smoke checks | writing full suite instead of smoke | `02,03,04` | `smoke-tests` |
| `bootstrap-repo.md` | scaffold new repo | choose manifest, choose archetype, choose stack, apply templates | repo purpose known | initial file skeleton | over-bootstrapping unused layers | `00,04,06,09,10` | templates + prompt-first examples |
| `generate-prompt-sequence.md` | build ordered prompt packs | define operator path, sequence prompts, add guide | prompt-first archetype | prompt files + docs | unclear sequence or duplicate prompts | `06,07,09` | `prompt-first` |
| `post-flight-refinement.md` | harden after first implementation pass | audit outputs, tighten docs/tests, retire weak patterns | first pass exists | refined prompts/docs/tests | endlessly reopening architecture | `00,05,06,08` | prompt and smoke examples |
| `add-deployment-support.md` | package for deploy | choose deploy path, add Procfile/config, verify env and storage | service exists | deploy files + docs | premature infra complexity | `04,10,11` | `dokku-deployment` |
| `add-seed-data.md` | add deterministic dev/test seed flows | define seed model, isolate dev/test, script resets | persistence exists | seed/reset commands | sharing dev/test data paths | `02,04` | `seed-data` |
| `add-api-endpoint.md` | add route/handler | schema, handler, wiring, tests, smoke | backend stack known | new endpoint | skipping response contracts | `01,02,03` | `api-endpoints` |
| `extend-cli.md` | add command/subcommand | command shape, parser wiring, output, tests | cli exists | new CLI command | unstable UX and flags | `01,02,03` | `cli` |
| `add-local-rag-indexing.md` | add indexing/retrieval flow | source ingest, chunking, indexing, retrieval check | local-rag archetype or target | index pipeline + smoke | vague metadata model | `02,03,04,07` | `local-rag` |
| `add-storage-integration.md` | add db/search/queue integration | define boundary, wire client, add infra, add tests | storage target known | integration + infra + tests | mock-only coverage | `02,03,04,10,11` | `storage-integration`, `docker-compose` |

## SECTION 8 - Stack pack design

### Primary backend stacks

| Stack pack | Purpose | Expected structure | Typical change surfaces | Common mistakes | Testing and smoke expectations | Integration expectations | Local infra rules | Deployment notes | Canonical examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `python-fastapi-polars-htmx-plotly.md` | Python backend/API and HTMX/Plotly services | `app/` or `src/`, routers, schemas, services, tests | endpoints, services, transforms, templates | using Flask-like patterns, skipping `uv`, missing `orjson`/Polars usage where relevant | route tests, service tests, smoke for startup/health and key path | real Docker-backed tests when Postgres/Redis/Mongo/Search touched | `docker-compose.yml`, `docker-compose.test.yml`, repo-derived `name:`, non-default ports, separate test data roots | strong Dokku fit for single service | endpoint, smoke, seed, docker, dokku |
| `typescript-hono-bun-drizzle-tsx.md` | lightweight TS backend with HTMX/tailwind/Plotly-friendly rendering | `src/`, routes, db, views, tests | routes, handlers, Drizzle schema, server entry | Express assumptions, npm-first drift, weak test isolation | smoke for startup and core route, tests for handlers and schema-adjacent logic | real infra tests when DB/cache/search touched | same compose and isolation rules; separate port band from dev | strong Dokku fit | endpoint, smoke, storage, dokku |
| `rust-axum.md` | modern Rust service stack | `src/`, handlers, state, tests | routes, extractors, middleware, storage clients | overengineering crates, missing integration path | cargo tests plus smoke path | real infra tests for persistence and queues | explicit non-default ports and isolated test compose stack | Dokku fit if packaging is simple | endpoint, smoke, docker |
| `go-echo-templ.md` | Go web/API service with templ views | `cmd/`, `internal/`, `web/`, tests | handlers, middleware, templ components | chi-oriented drift, weak templ examples | go tests plus smoke for startup and route | real infra tests for DB/queue/search boundaries | same compose rules; explicit port bands | strong Dokku fit | endpoint, HTMX, smoke, dokku |
| `elixir-phoenix.md` | Phoenix web/API service | `lib/`, `test/`, templates/components | controllers, contexts, channels, LiveView | overloading LiveView where static HTMX-like flow is enough, weak fixture isolation | mix test plus smoke for startup and critical route | real infra tests for DB/search/queue | same compose rules, explicit non-default host ports, separate test DB and volume names | Dokku fit if app is small and packaging remains clear | deployment, smoke, seed |

### Extension-path backend candidates

`backend-extension-candidates.md` should cover Nim/Jester/HappyX, Zig/Zap/Jetzig, Scala/Tapir/http4s/ZIO, Clojure/Kit/next.jdbc/Hiccup, Kotlin/http4k/Exposed, Crystal/Kemal/Avram, OCaml/Dream/Caqti/TyXML, and Dart/Dart Frog as architecturally compatible future additions.

For each candidate, the pack should define:

- where code usually lives
- likely test surface
- likely compose/deploy shape
- common assistant failure mode
- whether the candidate is v1-ready or future-path only

### Infra and storage packs

| Stack pack | Purpose | Typical changes | Common mistakes | Testing and smoke expectations | Local infra expectations | Canonical examples |
| --- | --- | --- | --- | --- | --- | --- |
| `redis-mongodb.md` | cache/document storage integrations | connection config, repositories, caching, aggregation | forgetting seed/reset isolation and index setup | smoke for connectivity and key happy path; real infra tests for reads/writes | separate dev/test services, volumes, env files, ports | storage integration, compose, seed |
| `trino-duckdb-polars.md` | analytics and local data experimentation | ETL flows, query layers, catalog config | treating Trino as same as DuckDB; skipping data reproducibility | smoke query against test catalog; integration for transform outputs | isolated catalog config and test datasets | pipeline, storage, docker |
| `nats-jetstream-meilisearch.md` | queue + lightweight search flows | publishers, consumers, indexing, search APIs | mock-only queue tests, missing durable stream config | smoke publish/consume and index/search happy path | separate streams/indexes for dev/test | storage, smoke |
| `timescaledb-elasticsearch-qdrant.md` | time-series, search, vector integrations | migrations, indexers, retrieval/search flows | blending search and source-of-truth responsibilities | smoke for startup and one query/index path; real infra tests for writes/reads | isolated test DB/index/collection names | storage, local-rag, docker |
| `docker-compose-dokku.md` | local infra and Dokku packaging conventions | compose files, Dockerfiles, Procfiles, deploy docs | default ports, non-isolated test data, Traefik-first assumptions | smoke for startup and deploy packaging check | conventional filenames, repo-derived `name:`, non-default bands, separate `.env` and `.env.test`, separate data paths | docker, dokku, smoke |

## SECTION 9 - Archetype pack design

| Archetype | Purpose | Likely stacks | Required doctrine | Required workflows | Recommended examples | Recommended scripts | Recommended smoke tests | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `prompt-first-repo` | ordered prompt workflows and operator context | prompt-first support plus optional polyglot subprojects | `00,06,07,08,09` | `bootstrap-repo`, `generate-prompt-sequence`, `post-flight-refinement` | prompt-first | link checker, bundle preview | prompt sequence lint or doc presence smoke | do not bury operator flow in giant README |
| `backend-api` | API/web service | FastAPI, Hono, Axum, Echo, Phoenix | `00,01,02,03,04,09` | `add-feature`, `add-api-endpoint`, `fix-bug`, `add-smoke-tests` | api-endpoints, smoke-tests | manifest validation | startup, health, key route | do not skip contract tests |
| `cli-tool` | command-line utility | Python or other single-binary/service-light stacks | `00,01,02,03,06,09` | `extend-cli`, `fix-bug`, `add-smoke-tests` | cli | bundle preview | help output, one happy-path command | do not add server-only assumptions |
| `data-pipeline` | ETL/batch systems | Python Polars, DuckDB, Trino | `00,02,03,04,06,09` | `add-feature`, `add-seed-data`, `add-smoke-tests` | seed-data, pipeline, docker | stale example detection | sample run, output existence, reset flow | do not let fixtures pollute dev data |
| `local-rag-system` | local indexing and retrieval | FastAPI plus Qdrant, Elasticsearch, DuckDB | `00,02,03,04,07,09,10` | `add-local-rag-indexing`, `add-storage-integration`, `add-smoke-tests` | local-rag, storage | bundle preview, link checker | ingest smoke, query smoke | define metadata model early |
| `multi-storage-experiment` | compare and combine storage engines | Trino, DuckDB, Redis, Mongo, Elastic, Qdrant, Timescale | `00,02,03,04,09,11` | `add-storage-integration`, `add-seed-data`, `refactor` | storage, docker | manifest validator | service-start and one happy-path query per system | avoid turning experiment into production architecture by default |
| `polyglot-lab` | multiple languages intentionally | combinations of all primary stacks | `00,01,04,06,09` | `bootstrap-repo`, `refactor`, `post-flight-refinement` | prompt-first, docker | alias lint, bundle preview | one smoke per subproject | do not load every stack for one task |
| `dokku-deployable-web-service` | small web service packaged for Dokku | FastAPI, Hono, Echo, Phoenix, Axum | `00,04,10,11` | `add-deployment-support`, `add-smoke-tests` | dokku, docker | deploy checker | health route and packaging smoke | do not assume Traefik or orchestration-first deployment |

## SECTION 10 - Task router and friendly alias system

### Router files

- `context/router/task-router.md`
- `context/router/stack-router.md`
- `context/router/archetype-router.md`
- `context/router/alias-catalog.md`

### Router behavior

- use verbs to infer workflow
- use nouns to infer stack and archetype
- confirm with manifest and repo signals
- load smallest relevant bundle first
- stop on ambiguity rather than inventing

### Alias strategy

The alias catalog maps normal English to internal doc names. Example:

| Normal request fragment | Internal mapping |
| --- | --- |
| "add route" | workflow `add-api-endpoint` |
| "make it deploy on Dokku" | workflow `add-deployment-support`, stack `docker-compose-dokku` |
| "wire Redis" | workflow `add-storage-integration`, stack `redis-mongodb` |
| "generate prompts" | workflow `generate-prompt-sequence`, archetype `prompt-first-repo` |
| "add a command" | workflow `extend-cli`, archetype `cli-tool` |

### Machine-readable router metadata

Recommended later addition:

- `manifests/router.aliases.yaml`
- `manifests/router.task-map.yaml`

These can mirror the markdown router docs without replacing them.

### Request mapping examples

| Request | Load bundle |
| --- | --- |
| "Add a `/metrics/daily` endpoint to the FastAPI service." | workflow `add-api-endpoint`; archetype `backend-api`; stack `python-fastapi-polars-htmx-plotly`; examples `api-endpoints`, `smoke-tests` |
| "Refactor the Bun service to isolate dev and test compose volumes." | workflow `refactor`; stack `typescript-hono-bun-drizzle-tsx`, `docker-compose-dokku`; doctrine `04` |
| "Create a prompt sequence for post-flight hardening." | workflows `generate-prompt-sequence`, `post-flight-refinement`; archetype `prompt-first-repo`; examples `prompt-first` |
| "Add Qdrant-backed retrieval to the local RAG repo." | workflow `add-local-rag-indexing`; archetype `local-rag-system`; stack `timescaledb-elasticsearch-qdrant`; examples `local-rag`, `storage-integration` |
| "Seed test data for Mongo and make sure dev data stays untouched." | workflow `add-seed-data`; stack `redis-mongodb`; doctrine `04`; examples `seed-data` |
| "Package this Echo app for Dokku and keep smoke coverage." | workflow `add-deployment-support`; archetypes `backend-api`, `dokku-deployable-web-service`; stacks `go-echo-templ`, `docker-compose-dokku`; examples `dokku-deployment`, `smoke-tests` |

## SECTION 11 - Manifest/profile system

### Recommended schema

```yaml
schema_version: 1
kind: context_profile
name: Backend API FastAPI Polars
slug: backend-api-fastapi-polars
summary: FastAPI plus Polars backend starter profile.
archetypes:
  - backend-api
stacks:
  - python-fastapi-polars-htmx-plotly
compatible_workflows:
  - add-feature
  - add-api-endpoint
  - add-smoke-tests
required_context:
  doctrine:
    - context/doctrine/00-core-principles.md
    - context/doctrine/02-testing-philosophy.md
  workflows:
    - context/workflows/add-api-endpoint.md
  archetypes:
    - context/archetypes/backend-api.md
  stacks:
    - context/stacks/python-fastapi-polars-htmx-plotly.md
optional_context:
  doctrine:
    - context/doctrine/04-compose-port-isolation.md
load_order:
  - README.md
  - AGENT.md
  - manifests/repo.profile.yaml
trigger_words:
  - fastapi
  - polars
preferred_examples:
  - examples/canonical/api-endpoints
anti_patterns:
  - mock-only persistence testing
bootstrap_defaults:
  compose:
    dev_file: docker-compose.yml
    test_file: docker-compose.test.yml
    dev_name_pattern: "<repo_slug>"
    test_name_pattern: "<repo_slug>-test"
  ports:
    dev_band: "18100-18199"
    test_band: "28100-28199"
  isolation:
    dev_env_file: .env
    test_env_file: .env.test
    dev_data_root: ./.data/dev
    test_data_root: ./.data/test
    separate_seed_flows: true
```

### Required fields

- `schema_version`
- `kind`
- `name`
- `slug`
- `summary`
- `archetypes`
- `stacks`
- `required_context`
- `load_order`
- `trigger_words`
- `bootstrap_defaults`

### Optional fields

- `compatible_workflows`
- `optional_context`
- `repo_signals`
- `preferred_examples`
- `anti_patterns`
- `dokku`

### Example profiles

V1 should ship at least these profiles:

1. `backend-api-fastapi-polars.yaml`
2. `backend-api-typescript-hono-bun.yaml`
3. `backend-api-rust-axum.yaml`
4. `backend-api-go-echo.yaml`
5. `webapp-elixir-phoenix.yaml`
6. `prompt-first-meta-repo.yaml`
7. `local-rag-base.yaml`
8. `multi-storage-zoo.yaml`
9. `cli-python.yaml`
10. `data-pipeline-polars.yaml`
11. `dokku-deployable-fastapi.yaml`
12. `dokku-deployable-typescript-hono-bun.yaml`
13. `dokku-deployable-go-echo.yaml`
14. `dokku-deployable-phoenix.yaml`

### Load order semantics

- `required_context` is the first bundle for that profile.
- `optional_context` is only loaded if the task clearly needs it.
- `preferred_examples` are consulted before inventing new patterns.

## SECTION 12 - Canonical examples strategy

### What makes an example canonical

- it reflects an actively preferred pattern
- it is small enough to imitate directly
- it matches current doctrine and stack guidance
- it includes the expected verification shape

### How many examples to keep

- one preferred example per pattern family
- at most one secondary active example per family when stack variation demands it
- retire the rest

### How to mark preferred examples

Use a short index file or manifest metadata with:

- `status: preferred`
- `pattern_family: api-endpoint`
- `stack: python-fastapi-polars-htmx-plotly`

### How to retire outdated examples

- move them to `examples/retired/`
- annotate why they were retired
- never let them appear as default examples

### How to avoid conflicting examples

- do not keep two equally endorsed examples for the same pattern family and stack
- split examples by pattern family and stack when necessary

### Recommended example layout

```text
examples/canonical/
├── README.md
├── api-endpoints/
├── smoke-tests/
├── docker-compose/
├── dokku-deployment/
├── cli/
├── prompt-first/
├── seed-data/
├── storage-integration/
└── local-rag/
```

## SECTION 13 - Templates strategy

### Templates to keep

- `templates/base/AGENT.md`
- `templates/base/CLAUDE.md`
- `templates/base/README.md`
- `templates/manifests/repo.profile.template.yaml`
- `templates/prompt-first/`
- `templates/fastapi/`
- `templates/hono-bun/`
- `templates/rust-axum/`
- `templates/go-echo/`
- `templates/phoenix/`
- `templates/dokku/`
- `templates/smoke-tests/`
- `templates/seed-data/`

### Templates vs examples

| Templates | Examples |
| --- | --- |
| meant to be copied and customized | meant to be studied and imitated |
| minimal and composable | concrete and opinionated |
| may contain placeholders | should look like realistic final patterns |

### Template discipline

- keep templates small
- compose templates instead of creating giant all-in-one starters
- do not let templates drift into full sample apps

## SECTION 14 - Script and automation strategy

| Script | What it does | Inputs | Outputs | Best language | Timing |
| --- | --- | --- | --- | --- | --- |
| `validate_manifests.py` | schema and path validation | manifest files | pass/fail + errors | Python | v1 |
| `validate_router_refs.py` | ensure router targets exist | router docs | pass/fail + missing refs | Python | v1 |
| `detect_stale_examples.py` | find examples no longer referenced or marked stale | example dirs + manifests | report | Python | phase 2 |
| `build_repo_from_profile.py` | compose templates into a starter repo | chosen profile + templates | generated repo skeleton | Python | phase 2 |
| `preview_context_bundle.py` | show what a request would load | request text + profile | ordered file list | Python | v1 |
| `generate_agent_files.py` | build repo-specific routers from template + profile | profile | `AGENT.md` and `CLAUDE.md` | Python | phase 2 |
| `lint_alias_collisions.py` | detect ambiguous alias mappings | alias catalog | report | Python | phase 2 |
| `check_internal_links.py` | verify docs references | docs tree | pass/fail + broken links | Python | v1 |

## SECTION 15 - Smoke-test and integration-test philosophy and starter strategy

### Smoke tests across archetypes

| Archetype | Minimal smoke test |
| --- | --- |
| API service | start app, hit health, hit one core route |
| CLI tool | run help and one core happy-path command |
| data pipeline | run one small batch and verify expected output artifact |
| local RAG | ingest one sample source and answer one retrieval query |
| Dokku-deployable service | start packaged app and hit health route |

### Minimal real-infra integration tests

Significant features require real Docker-backed integration tests when they touch:

- persistence
- queues
- search indexes
- vector stores
- cross-service boundaries

These tests should be mostly happy-path with a few reasonable edge cases.

### How smoke differs from unit and integration tests

| Test type | Purpose |
| --- | --- |
| unit | logic-level correctness |
| smoke | fast "does the thing start and basically work" signal |
| integration | real infra boundary verification |

### Starter asset organization

- `smoke-tests/api/`
- `smoke-tests/cli/`
- `smoke-tests/pipeline/`
- `smoke-tests/rag/`
- `smoke-tests/deploy/`

### When assistants should add or update smoke tests

- new endpoint
- new CLI command
- changed startup or health behavior
- changed seed/reset flow
- changed deploy packaging

### When assistants should add or update real-infra integration tests

- any significant persistence feature
- queue/search/vector integration
- new cross-service behavior
- anything where mocks would not prove operational correctness

## SECTION 16 - Dokku-oriented deployment doctrine

### Why Dokku fits many future repos

- many future projects are small services or small web apps
- Dokku keeps deploy operations simple
- Procfile and app config are easier to reason about than orchestration-heavy setups

### Conventions to adopt

- include a `Procfile` when Dokku is likely
- keep runtime env config explicit
- document persistent storage needs plainly
- avoid assuming a reverse proxy system more elaborate than needed

### Example files and templates

- `templates/dokku/Procfile`
- `templates/dokku/app.json`
- canonical Dokku deployment example

### How to think about config and persistence

- treat env vars as explicit inputs
- document volumes and storage mounts clearly
- keep build and release steps simple

### When Dokku is better than more elaborate setups

- single service
- small service plus one or two backing services
- operator wants low ceremony deployment

### When Dokku is not the right fit

- many independently scaling services
- highly dynamic service mesh needs
- orchestration-first operational requirements

## SECTION 17 - Example future project scenarios

| Project | Goal | Archetype | Stack | Required bundles | Manifest | Key examples | Dokku relevance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Market Pulse API | serve daily metrics over FastAPI and Polars | backend-api | FastAPI + Polars | doctrine `00,02,03,04`; workflow `add-api-endpoint`; stack `python-fastapi-polars-htmx-plotly` | `backend-api-fastapi-polars` | api-endpoints, smoke-tests, seed-data | high |
| Hono Ops Console | lightweight HTMX admin service | backend-api | Hono + Bun + Drizzle + TSX | doctrine `00,02,03,04`; workflow `add-feature`; stack `typescript-hono-bun-drizzle-tsx` | `backend-api-typescript-hono-bun` | api-endpoints, smoke-tests, docker | high |
| Axum Stream API | Rust event/status API | backend-api | Rust + Axum | doctrine `00,02,03`; workflow `add-api-endpoint`; stack `rust-axum` | `backend-api-rust-axum` | api-endpoints, smoke-tests | medium |
| Echo Plot Board | Go web app with templ and Plotly | backend-api | Go + Echo + templ | doctrine `00,02,03,04`; workflow `add-feature`; stack `go-echo-templ` | `backend-api-go-echo` | smoke-tests, docker, dokku | high |
| Phoenix Signals | Phoenix-based interactive service | dokku-deployable-web-service | Elixir + Phoenix | doctrine `00,04,10`; workflow `add-deployment-support`; stack `elixir-phoenix` | `webapp-elixir-phoenix` | dokku, smoke-tests | high |
| Prompt Forge | meta-runner prompt repo | prompt-first-repo | prompt-first support | doctrine `00,06,07,08,09`; workflows `bootstrap-repo`, `generate-prompt-sequence` | `prompt-first-meta-repo` | prompt-first | low |
| Local Corpus Lab | local document retrieval tool | local-rag-system | FastAPI + Qdrant + DuckDB | doctrine `00,02,03,04,07`; workflows `add-local-rag-indexing`, `add-storage-integration` | `local-rag-base` | local-rag, storage-integration, smoke-tests | medium |
| Storage Zoo | compare Redis, Mongo, Trino, DuckDB, Qdrant | multi-storage-experiment | multiple data stacks | doctrine `00,02,03,04,11`; workflow `add-storage-integration` | `multi-storage-zoo` | storage-integration, docker | low |
| Polars CLI Runner | local data CLI | cli-tool | Python + Polars | doctrine `00,01,02,03`; workflow `extend-cli` | `cli-python` | cli, smoke-tests | low |
| Batch Melt | scheduled ETL pipeline | data-pipeline | Python + Polars + DuckDB | doctrine `00,02,03,04`; workflows `add-feature`, `add-seed-data` | `data-pipeline-polars` | seed-data, smoke-tests | low |
| FastAPI Dokku Starter | deployable single-service API | dokku-deployable-web-service | FastAPI + Docker | doctrine `00,04,10,11`; workflow `add-deployment-support` | `dokku-deployable-fastapi` | dokku, docker, smoke-tests | high |
| Bun Dokku Starter | deployable Hono service | dokku-deployable-web-service | Hono + Bun | doctrine `00,04,10,11`; workflow `add-deployment-support` | `dokku-deployable-typescript-hono-bun` | dokku, smoke-tests | high |

## SECTION 18 - Cross-model guidance

### One shared system, three model styles

| Area | Codex | Claude | Gemini |
| --- | --- | --- | --- |
| routing style | explicit and procedural | concise but can tolerate a bit more rationale | explicit metadata and short factual cues |
| preferred doc size | small | small to medium | small |
| example usage | strong | strong | very strong |
| likely failure | over-implementation or stack drift | over-reading or over-explaining | vague inference without explicit metadata |
| response style | action-oriented | explanatory when needed | terse and metadata-driven |

### How to reduce model-specific drift

- keep one shared doctrine layer
- keep router files deterministic
- let manifests carry machine-readable hints
- let examples anchor implementation
- avoid assistant-specific forks unless the top-level router wording truly needs it

## SECTION 19 - Quality rubric

Score each area from 1 to 5.

| Area | 1 | 3 | 5 |
| --- | --- | --- | --- |
| clarity | vague names and overlapping docs | mostly clear | deterministic names and clean boundaries |
| routing quality | assistant must guess heavily | some routing hints | strong natural-language inference and stop rules |
| doctrine quality | generic slogans | useful but uneven | durable actionable doctrine with real constraints |
| workflow usefulness | incomplete task steps | decent task guidance | clear sequences, outputs, pitfalls, references |
| stack specificity | generic framework notes | moderate detail | concrete change surfaces and verification expectations |
| archetype usefulness | barely differentiated | usable | clearly shapes task behavior and example choice |
| canonical example quality | random examples | some preferred examples | one strong preferred example per pattern family |
| anti-sprawl protection | bulk loading common | some guardrails | smallest-bundle discipline is encoded everywhere |
| bootstrap readiness | hard to start new repo | workable | clear templates, manifests, scripts, and docs |
| frontier-model friendliness | inconsistent across models | acceptable | shared deterministic system works across Codex/Claude/Gemini |
| maintainability | docs drift fast | manageable | scoped docs, validation scripts, retirement paths |

## SECTION 20 - Deliverables for the first implementation pass

### Mandatory v1 files

- `README.md`
- `AGENT.md`
- `CLAUDE.md`
- `docs/agent-context-architecture.md`
- `context/router/task-router.md`
- `context/router/stack-router.md`
- `context/router/archetype-router.md`
- `context/router/alias-catalog.md`
- core doctrine docs already present
- core workflow docs already present
- core stack docs already present
- core archetype docs already present
- `manifests/README.md`
- `manifests/repo.profile.yaml`
- v1 profile manifests

### Mandatory v1 manifests

- `backend-api-fastapi-polars.yaml`
- `backend-api-typescript-hono-bun.yaml`
- `backend-api-rust-axum.yaml`
- `backend-api-go-echo.yaml`
- `webapp-elixir-phoenix.yaml`
- `prompt-first-meta-repo.yaml`
- `local-rag-base.yaml`
- `multi-storage-zoo.yaml`
- `cli-python.yaml`
- `data-pipeline-polars.yaml`
- `dokku-deployable-fastapi.yaml`
- `dokku-deployable-typescript-hono-bun.yaml`

### Mandatory v1 examples

- canonical API endpoint example
- canonical smoke test example
- canonical Docker Compose isolation example
- canonical Dokku deployment example
- canonical prompt-first example
- canonical seed data example
- canonical storage integration example
- canonical local RAG example

### Mandatory v1 templates

- base `AGENT.md`
- base `CLAUDE.md`
- base `README.md`
- repo profile template
- FastAPI starter
- Hono/Bun starter
- Go/Echo starter
- Dokku starter
- smoke-test starter

### Phase 2 automation

- repo builder from profile
- agent file generator
- stale example detection
- alias collision lint

### Strong but realistic v1

V1 should not try to fully scaffold every future stack. A strong v1 delivers:

- deterministic routing
- doctrine/workflow/stack/archetype separation
- manifest schema and several high-value profiles
- a minimal canonical example set
- basic validation scripts
- Dokku-ready conventions
- dev/test Compose isolation rules encoded clearly

### Recommended first commit sequence

1. `docs: lock base repo purpose, architecture, and routing doctrine`
2. `docs: replace top-level assistant routers with deterministic minimal loaders`
3. `docs: add task, stack, archetype routers and alias catalog`
4. `docs: standardize manifest schema and repo profile`
5. `feat: add v1 starter profile manifests`
6. `docs: expand canonical example and template strategy references`
7. `feat: add manifest and router validation helpers`
8. `docs: add quality rubric and bootstrap checklist refinements`
