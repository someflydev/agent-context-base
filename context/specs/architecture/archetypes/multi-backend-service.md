---
acb_origin: canonical
acb_source_path: context/specs/architecture/archetypes/multi-backend-service.md
acb_role: architecture
acb_archetypes: [multi-backend-service]
acb_version: 1
---

## Multi-Backend Architecture

Service seams must be versioned and documented. Each backend should own a clearly named contract, runtime, and storage responsibility.

Prefer explicit REST, gRPC, or event boundaries over ad hoc shared-database coupling unless the repo is intentionally exploring that as a controlled experiment.
