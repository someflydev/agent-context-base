# Context Evolution

This changelog records durable architectural changes to the base itself.

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
