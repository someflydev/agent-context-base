# Context Evolution

This changelog records durable architectural changes to the base itself.

## 2026-03-18: 100-Example Catalog, Derived Examples, and Extended Verification

- added `EXAMPLE_PROJECTS` (100 entries, #1–#100) and `ExampleProject` dataclass to `new_repo.py`; `--use-example N` now pre-fills archetype, stack, and flags from the catalog entry
- added `--list-examples` flag to browse the full catalog grouped by category
- added three new archetypes (`data-acquisition-service`, `multi-source-sync-platform`, `multi-backend-service`) and three new stacks (`qdrant`, `duckdb-trino-polars`, `redis-keydb-mongo`) to `new_repo.py`
- added `examples/derived/example-prompts.yaml` (101 entries, #1–#101) with per-example prompts, archetypes, stacks, and `new_repo_args`
- added `examples/derived/derived-examples.yaml` with 8 sub-group cluster guides (4 Team A, 4 Team B)
- added `examples/derived/spin-outs.yaml` with 10 spin-out platform entries (team_a, team_b, cross_team)
- added `examples/derived/tier-rankings.yaml` with 5 tiers covering all 100 examples by composability score
- added `examples/derived/orchestration-strategies.yaml` with 5 named coordination patterns
- added `--list-derived` flag to `new_repo.py` to print sub-groups and spin-out platforms in aligned columns
- added `--derived-example NAME` flag to `new_repo.py` to print the cluster guide for any sub-group or spin-out, including source examples and scaffold commands
- added `verification/examples/derived/test_derived_coverage.py` (24 tests) covering: example-prompts count and structure, derived-examples team split and field completeness, spin-outs field completeness and origin validity, tier coverage of all 100 examples, and orchestration-strategy field completeness
- registered `test_derived_coverage` in `HEAVY_MODULES` of `run_verification.py`

## 2026-03-17: Cognitive Skills Layer

- added four new skills covering the previously uncovered boot-sequence steps: `manifest-selection.md` (step 5), `context-bundle-assembly.md` (step 6), `verification-path-selection.md` (step 8), and `memory-continuity-discipline.md` (steps 3 and 8)
- all four skills are now named in the bootstrap workflow copy sequence and carried into generated repos in full
- task router updated with load triggers for all four skills; alias catalog gains a `skills:` section with short-form aliases
- both generated-repo templates (`CLAUDE.template.md`, `AGENT.template.md`) now include a pointer to `context/skills/` so assistants booting in derived repos discover the directory
- contributor playbook Section 7 now names skills as a first-class artifact type with format rules; Section 10 extension checklist updated
- `docs/repo-layout.md` gains a `context/skills/` row; `docs/ARCHITECTURE_MAP.md` Component Index and Context System Map updated to include the skills layer

## 2026-03-17: CUJ Playwright Tests for Backend-Driven UI

- added 10 critical user journey (CUJ) Playwright tests using a page object model, covering load, apply filter, clear filter, multi-select, exclude, keyword search, sort, scroll, count verification, and reset-all flows
- added verification unit tests for search correctness, sort order, RULE 1 and RULE 2 under search, and fingerprint assertions
- added CUJ test section to the task router so queries about end-to-end UI verification route to the correct workflow
- updated alias catalog to resolve CUJ-related aliases to the Playwright verification workflow

## 2026-03-17: Text Search, Sort, and Scroll Layout Expansion

- added doctrine for text search query correctness, sort order determinism, and scroll layout discipline
- added workflows for adding text search, sort order controls, and infinite-scroll or pagination layouts to backend-driven UI surfaces
- added Python/FastAPI reference implementation demonstrating search, sort, and scroll patterns with a Playwright verification suite
- added Playwright single-feature tests for search+sort (search returns correct rows, sort reorders deterministically) and split filter panel (include/exclude facet behavior)
- extended text search, sort, and scroll layout guidance to all active application stacks: FastAPI, Phoenix, Go/Echo, TypeScript/Hono, Rust/Axum, Ruby/Hanami, Clojure/Kit, Kotlin/http4k, Scala/Tapir, Crystal/Kemal, Dart/Dartfrog, OCaml/Dream, Nim/Jester, Zig/Zap
- updated example registry, stack router, and stack docs to reflect new cross-language correctness coverage

## 2026-03-17: Python ML Library Doctrine

- added Python ML and data science library selection doctrine covering scikit-learn, XGBoost, LightGBM, statsmodels, sentence-transformers, and supporting libraries
- updated the Python/FastAPI stack doc to reference the ML doctrine as the canonical selection guide for ML inference endpoints
- updated router and alias catalog to route ML stack queries to the doctrine before the stack pack

## 2026-03-17: DuckDB+Parquet Local Stack

- added `context/stacks/duckdb-parquet.md` as a standalone local-file analytical stack doc covering DuckDB+Parquet round-trip patterns, query discipline, and local data lake structure
- added a canonical DuckDB+Parquet local round-trip example demonstrating file write, DuckDB query, and result assertion
- updated example registry and stack router to resolve DuckDB+Parquet queries to the new dedicated stack doc

## 2026-03-14: Database Stack Coverage Expansion

- added solo stack packs for `mongo`, `redis`, `trino`, and `postgresql`
- `postgresql.md` is now the baseline transactional SQL pack that many backend repos implicitly assumed without a dedicated context file
- `redis.md` covers data-structure selection, TTL discipline, key naming, and credible use cases independently of MongoDB
- `mongo.md` covers aggregation pipelines, partial indexes, request/response log retention patterns, and document-shape discipline
- `trino.md` covers federated analytics routing, compatible catalog constraints, pushdown risks, and cross-catalog query patterns
- narrowed `redis-keydb-mongo.md` to mixed-storage and comparison decisions; solo requests now route to dedicated solo packs
- narrowed `duckdb-trino-polars.md` to repos that genuinely use all three tools together; Trino is now independently discoverable
- updated `timescaledb.md` to explicitly pair with `postgresql.md` as its foundational layer
- updated stack router, alias catalog, repo-signal hints, and task router to resolve solo database requests to solo packs
- registered `mongo`, `redis`, `trino`, `postgresql` as valid stack identifiers in `manifest_tools.py`
- updated `multi-storage-zoo.yaml` to surface `postgresql` as a secondary stack and the new solo packs as optional context

## 2026-03-14: Backend-Driven UI Correctness Expansion

- added doctrine for backend-driven HTMX, Tailwind, and Plotly correctness
- added workflows for faceted filters, include/exclude state, dynamic counts, Plotly-backed query views, and Playwright verification
- added router, alias, and manifest hooks for backend-driven UI queries
- added canonical examples and verification for filter-count and chart-state alignment

## 2026-03-13: Documentation Refactor

- rewrote the root README as the front-facing entrypoint
- reduced `AGENT.md` and `CLAUDE.md` to fast boot docs
- compressed overlapping docs into a smaller architecture and usage hierarchy
- simplified the visual model to a few diagrams that match the actual runtime, generation, verification, and multi-agent patterns
- aligned the generated-repo templates with the new boot guidance

## 2026-03-12: Reliability And Operations Pass

- added assistant anchors under `context/anchors/`
- added context weighting, repo-signal hints, and example ranking metadata
- added broader context validation and prompt-first repo analysis tooling
- tightened Compose naming, port allocation, and environment-isolation checks

## Earlier Milestones

- v2 introduced manifests, canonical example files, templates, and `scripts/new_repo.py`
- v1 established the split between doctrine, workflows, stacks, archetypes, and routers
