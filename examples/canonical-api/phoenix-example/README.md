# phoenix-example

Minimal Phoenix 1.7 mini-app demonstrating the canonical four-endpoint API surface using Bandit as the HTTP adapter, Jason for JSON encoding, and in-memory seed data — no Ecto, no database.

## Endpoints

- `GET /healthz` — JSON health snapshot
- `GET /api/reports/:tenant_id` — JSON report envelope
- `GET /fragments/report-card/:tenant_id` — HTML fragment (HTMX OOB)
- `GET /data/chart/:metric` — JSON chart payload

```
Verification level: smoke-verified
Harness: phoenix_min_app
Last verified by: verification/examples/elixir/test_phoenix_examples.py
```
