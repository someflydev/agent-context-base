---
acb_origin: canonical
acb_source_path: context/specs/product/archetypes/data-acquisition-service.md
acb_role: product
acb_archetypes: [data-acquisition-service]
acb_version: 1
---

## Data Acquisition Service Intent

The product exists to fetch, normalize, checkpoint, and persist external data safely. Raw-source behavior, normalization fidelity, and replay safety are part of the product truth.

Specs should distinguish fetch, parse, normalize, and persistence stages so assistants can change one stage without blurring the others.
