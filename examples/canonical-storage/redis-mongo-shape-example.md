# Redis And Mongo Shape Example

Verification level: structure-verified
Harness: none
Last verified by: verification/examples/data/test_storage_examples.py

Use explicit prefixes for dev and test data so resets stay isolated across both
Redis and MongoDB when the repo uses them together.

## When To Use This Example

Use this example when:

- the repo uses Redis AND MongoDB in the same service and the design question is
  how to isolate dev and test data across both simultaneously.

Use `redis-structures-example.md` when:

- the workload is Redis-only and the question is which Redis structure to use.

Use `mongo-weekly-reporting-example.md` when:

- the workload is MongoDB-only and the question is collection shape, index
  strategy, or aggregation pipelines.

## Redis Key Shapes

Key format: `<env>:<domain>:<tenant>:<report-id>`

```text
dev:report-runs:acme:daily-signups
test:report-runs:acme:daily-signups
```

The `dev:` prefix is used by the running application. The `test:` prefix is used
exclusively by integration tests. No test script may read or write under `dev:`.

For the full Redis structure taxonomy (sorted sets, hashes, streams, rate-limit
counters), see `redis-structures-example.md`.

## Redis Commands

Write a report-run status entry with a one-hour TTL:

```text
SET dev:report-runs:acme:daily-signups '{"status":"ready","tenant_id":"acme","report_id":"daily-signups","captured_at":"2026-03-01T00:00:00Z"}' EX 3600
SET test:report-runs:acme:daily-signups '{"status":"ready","tenant_id":"acme","report_id":"daily-signups","captured_at":"2026-03-01T00:00:00Z"}' EX 3600
```

List all keys under the test namespace (safe to call in test teardown):

```text
KEYS test:report-runs:*
```

Delete a specific test key:

```text
DEL test:report-runs:acme:daily-signups
```

Never issue `KEYS dev:*` or `DEL dev:*` from a test or teardown script.

## Mongo Collection Shape

Collection name: `report_runs`

Required fields:

- `tenant_id` — drives index selectivity
- `report_id` — identifies the report type
- `status` — current run state
- `payload_version` — bump when document shape changes
- `captured_at` — ISO 8601 UTC timestamp

Indexed fields: `tenant_id`, `report_id`, `captured_at`

For index strategy and aggregation pipeline patterns, see
`mongo-weekly-reporting-example.md`.

## Mongo Test Isolation

Test data lives in a separate database named `test_db`, not in the application
database (`app_db`). Tests insert fixture documents with a `_fixture: true` marker
so teardown can target them precisely without touching dev data.

Insert a fixture document:

```javascript
db.getSiblingDB("test_db").report_runs.insertOne({
  tenant_id: "acme",
  report_id: "daily-signups",
  status: "ready",
  payload_version: 2,
  captured_at: ISODate("2026-03-01T00:00:00Z"),
  _fixture: true
})
```

Teardown — remove only fixture documents:

```javascript
db.getSiblingDB("test_db").report_runs.deleteMany({ _fixture: true })
```

Alternatively, drop the entire test collection if the test owns it exclusively:

```javascript
db.getSiblingDB("test_db").report_runs.drop()
```

Never call `deleteMany` or `drop` against `app_db` from a test script.

## docker-compose.test.yml Snippet

Port offsets prevent test containers from colliding with dev containers:

```yaml
services:
  redis-test:
    image: redis:7-alpine
    ports:
      - "16379:6379"
    volumes:
      - redis-test-data:/data

  mongo-test:
    image: mongo:7
    ports:
      - "27018:27017"
    volumes:
      - mongo-test-data:/data/db

volumes:
  redis-test-data:
  mongo-test-data:
```

Dev Redis runs on `6379`; test Redis runs on `16379`.
Dev Mongo runs on `27017`; test Mongo runs on `27018`.

## Reset Rule

1. In test teardown, delete all Redis keys matching `test:*`.
2. In test teardown, drop or clear the test Mongo collection or database.
3. Never touch keys or collections under the `dev:` namespace from a test script.
4. CI pipelines must run test teardown even when tests fail.
