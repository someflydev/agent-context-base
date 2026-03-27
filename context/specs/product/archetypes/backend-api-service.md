---
acb_origin: canonical
acb_source_path: context/specs/product/archetypes/backend-api-service.md
acb_role: product
acb_archetypes: [backend-api-service]
acb_version: 1
---

## Backend API Service Intent

The product surface is an API or backend-driven fragment service with clear request, response, and persistence expectations. Handler behavior must stay narrow and explicit enough that validation can prove one route at a time.

The repo should prefer stable contracts over implied behavior. If interactive UI fragments exist, the backend contract that feeds them is still the primary product truth.
