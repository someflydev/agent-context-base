---
acb_origin: canonical
acb_source_path: context/validation/archetypes/backend-api-service.md
acb_role: validation
acb_archetypes: [backend-api-service]
acb_version: 1
---

## Backend API Validation

Prove the service boots, one representative route works, and one storage-backed path is correct when persistence is involved. Prefer route or request-level proof over vague “server started” claims.

Concrete proof posture:

- exercise `/health` or `/healthz`
- prove one non-trivial endpoint with exact status and payload assertions
- when persistence is involved, prove one real test-stack round-trip
