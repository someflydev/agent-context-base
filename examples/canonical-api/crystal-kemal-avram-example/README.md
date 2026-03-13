# Crystal Kemal Avram Runtime Example

Minimal runtime bundle for Docker-backed verification of the Crystal Kemal plus Avram canonical API surface.

Endpoints:

- `/healthz`
- `/api/reports/:tenant_id`
- `/fragments/report-card/:tenant_id`
- `/data/chart/:metric`

Verification level: smoke-verified  
Harness: crystal_kemal_avram_min_app  
Last verified by: verification/examples/crystal/test_crystal_kemal_avram_examples.py

Notes:

- the runnable bundle keeps Kemal bootable inside Docker without requiring Crystal on the host
- `shard.yml` includes both `kemal` and `avram` so dependency resolution is exercised even though the smoke runtime uses seeded in-memory data instead of a live Avram-backed database
