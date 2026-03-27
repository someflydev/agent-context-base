---
acb_origin: canonical
acb_source_path: context/validation/archetypes/multi-backend-service.md
acb_role: validation
acb_archetypes: [multi-backend-service]
acb_version: 1
---

## Multi-Backend Validation

Validate one real cross-service seam with concrete payload assertions. Do not treat isolated service-local tests as proof that the integrated system still works.

Use the real seam transport where possible: HTTP, gRPC, queue, or explicit in-process contract.
