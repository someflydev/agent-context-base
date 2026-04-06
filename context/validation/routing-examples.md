# Routing Examples

The examples below are illustrative `work.py route-check` outputs.
They are HEURISTIC examples, not golden snapshots.

## Scenario 1 Output

```text
Route Check (HEURISTIC)
=======================
Prompt:          "Add a paginated GET /products endpoint to the FastAPI service..."

Implied Capabilities:
  api, storage  (from keywords: fastapi, endpoint, postgres)

Candidate Archetypes:
  1. backend-api-service

Candidate Manifests:
  1. backend-api-fastapi-polars

Routing Decision (HEURISTIC):
  Primary Archetype:  backend-api-service
  Primary Manifest:   backend-api-fastapi-polars
  Budget Profile:     medium
  Confidence:         usable (0.76)
```

## Scenario 2 Output

```text
Route Check (HEURISTIC)
=======================
Prompt:          "Compare Qdrant versus Meilisearch for semantic search latency..."

Implied Capabilities:
  storage, rag, search  (from keywords: qdrant, meilisearch, search)

Candidate Archetypes:
  1. local-rag-system
  2. multi-storage-experiment

Candidate Manifests:
  1. local-rag-base

Routing Decision (HEURISTIC):
  Primary Archetype:  local-rag-system
  Primary Manifest:   local-rag-base
  Budget Profile:     large
  Confidence:         usable (0.76)

Warnings:
  - multi-backend comparison; cross-system profile may be appropriate
  - HEURISTIC: this is not a verified route, only a keyword-based suggestion
```

## Scenario 3 Output

```text
Route Check (HEURISTIC)
=======================
Prompt:          "Bootstrap a new data acquisition service that scrapes product..."

Implied Capabilities:
  api, storage, pipelines, scraping, workers, cloud-deployment

Candidate Archetypes:
  1. data-acquisition-service
  2. multi-source-sync-platform
  3. dokku-deployable-service

Candidate Manifests:
  1. data-acquisition-service
  2. multi-source-sync-platform
  3. dokku-deployable-fastapi

Routing Decision (HEURISTIC):
  Primary Archetype:  data-acquisition-service
  Primary Manifest:   data-acquisition-service
  Budget Profile:     cross-system
  Confidence:         strong (>= 0.85) (0.90)

Warnings:
  - 6 capabilities implied - expect a large context budget
  - cloud-deployment capability requires an explicit trigger
  - HEURISTIC: this is not a verified route, only a keyword-based suggestion
```
