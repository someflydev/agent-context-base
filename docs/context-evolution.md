# Context Evolution

This changelog records durable architectural changes to the base itself.

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
