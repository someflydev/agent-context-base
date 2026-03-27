---
acb_origin: canonical
acb_source_path: context/specs/architecture/archetypes/backend-api-service.md
acb_role: architecture
acb_archetypes: [backend-api-service]
acb_version: 1
---

## Backend API Architecture

Keep request handling, domain shaping, and persistence boundaries separate. Route files should decode inputs and encode outputs, while domain and storage behavior live behind explicit service seams.

Avoid leaking database, dataframe, or queue semantics directly through handlers unless the repo intentionally treats that as the public contract.
