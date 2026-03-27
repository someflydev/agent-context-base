## Data Acquisition Architecture

Separate source fetch, raw retention, normalization, classification or enrichment, and persistence. Rate-limit handling, retries, idempotency keys, and checkpoint state should live in explicit components.

The raw ingest path must remain inspectable so drift or source breakage can be diagnosed later.
