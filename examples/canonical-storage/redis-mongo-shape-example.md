# Redis And Mongo Shape Example

Use explicit prefixes for dev and test data so resets stay isolated.

Redis key shape:

```text
dev:report-runs:acme:daily-signups
test:report-runs:acme:daily-signups
```

Suggested payload:

```json
{
  "tenant_id": "acme",
  "report_id": "daily-signups",
  "status": "ready",
  "captured_at": "2026-03-01T00:00:00Z"
}
```

Mongo collection shape:

- collection: `report_runs`
- indexed fields: `tenant_id`, `report_id`, `captured_at`
- required fields:
  - `tenant_id`
  - `report_id`
  - `status`
  - `payload_version`

Reset rule:

- test reset scripts may delete `test:*` Redis keys and test Mongo fixture documents
- test reset scripts must never touch dev prefixes or dev Mongo data

