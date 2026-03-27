---
acb_origin: canonical
acb_source_path: context/specs/architecture/archetypes/data-acquisition-service.md
acb_role: architecture
acb_archetypes: [data-acquisition-service]
acb_version: 1
---

## Data Acquisition Architecture

Separate source fetch, raw retention, normalization, classification or enrichment, and persistence. Rate-limit handling, retries, idempotency keys, and checkpoint state should live in explicit components.

The raw ingest path must remain inspectable so drift or source breakage can be diagnosed later.
