# Juicy Prompt Scenarios

These canonical scenarios are HEURISTIC routing fixtures for
`python3 scripts/work.py route-check`.

## Scenario 1: Simple Single-Stack API Task

```text
Add a paginated GET /products endpoint to the FastAPI service that queries
a Postgres table and returns results with next_cursor for keyset pagination.
```

- Expected implied capabilities: `api`, `storage`
- Expected primary archetype: `backend-api-service`
- Expected primary manifest: `backend-api-fastapi-polars` or the closest
  FastAPI backend manifest
- Expected budget profile: `small` or `medium`
- Expected confidence: `usable` to `strong`
- Expected warnings: none significant
- Expected suggested bundle:
  - `AGENT.md`
  - `manifests/backend-api-fastapi-polars.yaml`
  - `context/archetypes/backend-api-service.md`
  - `context/workflows/add-api-endpoint.md`
  - `context/workflows/add-storage-integration.md`
  - `context/doctrine/context-complexity-budget.md`
  - one or two matching stack files such as the FastAPI and Postgres surfaces
- Healthy budget note:
  - A healthy route stays near `small` or `medium` and does not pull extra
    archetypes or unrelated workflow packs.
- Over-loaded note:
  - The route is over-loaded if it drags in deployment, eventing, RAG, or
    multi-backend context for a simple storage-backed endpoint.

## Scenario 2: Multi-Stack RAG Comparison

```text
Compare Qdrant versus Meilisearch for semantic search latency over 50K
product documents. Index the same dataset in both, run 20 queries, measure
p50 and p95 latency, and produce a short report.
```

- Expected implied capabilities: `storage`, `rag`, `search`
- Expected primary archetype: `local-rag-system` or
  `multi-storage-experiment`
- Expected primary manifest: `local-rag-base` or the closest retrieval-focused
  manifest
- Expected budget profile: `large` or `cross-system`
- Expected confidence: `usable`
- Expected warnings:
  - `multi-backend comparison; cross-system profile may be appropriate`
- Expected `is_likely_juicy`: `True`
- Expected suggested bundle:
  - `AGENT.md`
  - `manifests/local-rag-base.yaml`
  - `context/archetypes/local-rag-system.md`
  - `context/workflows/add-local-rag-indexing.md`
  - `context/workflows/add-storage-integration.md`
  - `context/doctrine/context-complexity-budget.md`
  - stack files for `qdrant` plus one comparison backend if available
- Healthy budget note:
  - A healthy route acknowledges the comparison boundary and keeps the bundle
    centered on retrieval plus storage proof paths.
- Over-loaded note:
  - The route is over-loaded if it treats the comparison as a full product
    bootstrap and loads deployment or unrelated interface stacks.

## Scenario 3: Full-Stack New Service Bootstrap

```text
Bootstrap a new data acquisition service that scrapes product prices from
3 e-commerce sites on a daily schedule, stores raw HTML in S3-compatible
storage, transforms prices into a Polars dataframe stored in DuckDB,
exposes a FastAPI /prices endpoint with Postgres persistence, and deploys
to Dokku.
```

- Expected implied capabilities:
  - `api`, `storage`, `pipelines`, `scraping`, `workers`,
    `cloud-deployment`
- Expected primary archetype: `data-acquisition-service`
- Expected primary manifest: `data-acquisition-service`
- Expected budget profile: `cross-system`
- Expected confidence: `strong`
- Expected warnings:
  - `6 capabilities implied - expect a large context budget`
  - `cloud-deployment capability requires an explicit trigger`
- Expected `is_likely_juicy`: `True`
- Expected suggested bundle:
  - `AGENT.md`
  - `manifests/data-acquisition-service.yaml`
  - `context/archetypes/data-acquisition-service.md`
  - workflow files for API, storage, parsing, scraping, recurring sync, and
    deployment support
  - `context/doctrine/context-complexity-budget.md`
  - deployment doctrine when Dokku is explicit
  - one or two stack files for the dominant FastAPI and analytical surfaces
- Healthy budget note:
  - A healthy route admits this is cross-system work and keeps the context
    explicit instead of pretending the task is single-stack.
- Over-loaded note:
  - The route is under-specified if it skips scraping, worker scheduling, or
    deployment doctrine, and over-loaded if it adds unrelated UI or RAG packs.
