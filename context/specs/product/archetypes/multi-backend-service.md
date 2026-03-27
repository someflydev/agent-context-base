---
acb_origin: canonical
acb_source_path: context/specs/product/archetypes/multi-backend-service.md
acb_role: product
acb_archetypes: [multi-backend-service]
acb_version: 1
---

## Multi-Backend Service Intent

The product is delivered through more than one backend process or language surface. The seam between those services is part of the product and must be specified like an interface, not treated as incidental plumbing.

Each service should own a distinct responsibility. Cross-service ambiguity is a spec defect because it makes autonomy unsafe.
