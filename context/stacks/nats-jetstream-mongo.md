# NATS JetStream + MongoDB

Use this pack when the repo implements a capture-enrich-persist pipeline:

```
Producer → NATS JetStream → Consumer/Enricher → MongoDB
```

The producer captures request/response events and publishes bounded, versioned payloads to NATS. A separate consumer process reads from NATS, validates, cleans, and enhances each message, then inserts the enriched document into MongoDB for reporting queries.

Load `context/stacks/nats-jetstream.md` for broker configuration detail. Load `context/stacks/mongo.md` for MongoDB collection naming, index strategy, and aggregation pipeline guidance.

## When To Load This Pack

- The repo produces events from one process and consumes them in a separate process (different scaling unit, different failure domain).
- The enrichment step cannot happen at publish time — it requires computed fields that depend on the full payload (e.g. response-time classification, error categorisation).
- MongoDB holds the enriched documents for reporting or aggregation queries.
- The pipeline needs durable delivery with retry and dead-letter handling.

## Typical Repo Surface

- `app/messaging/producer.py` — payload construction and NATS publish
- `app/messaging/consumer.py` — pull consumer loop, enrichment dispatch, ack/nack logic
- `app/enrichment/enricher.py` — validation, cleaning, field derivation
- `app/db/mongo.py` — MongoDB client, weekly collection naming helper
- `app/db/repositories/request_log_repo.py` — insert and query logic
- `tests/integration/test_pipeline.py` — full pipeline test: publish → consume → assert MongoDB document
- `docker-compose.test.yml` — `nats -js` + `mongo:7` services

## Producer Responsibilities

The producer constructs a **bounded payload** from the raw request/response. It must not store the raw HTTP body, unbounded arrays, or PII fields that do not belong in the reporting layer.

### Required Payload Fields

```json
{
  "payload_version": 1,
  "tenant_id": "acme",
  "report_id": "daily-signups",
  "correlation_id": "req-abc-123",
  "published_at": "2026-03-10T14:22:00Z",
  "request_method": "POST",
  "request_path": "/api/reports",
  "response_status": 200,
  "response_time_ms": 142,
  "source_ip_hash": "sha256:abcd1234"
}
```

### Publish

Publish to subject: `reports.requests.<tenant_id>.<report_id>`

```python
subject = f"reports.requests.{payload['tenant_id']}.{payload['report_id']}"
await js.publish(subject, json.dumps(payload).encode())
```

The producer does not wait for consumer confirmation. The stream provides durability — once the broker acknowledges the publish, the message is durable regardless of consumer availability.

### What NOT To Include in the Payload

- Raw HTTP request or response bodies
- Unbounded arrays (query results, list of items)
- PII fields that must not reach the reporting layer (email, IP address without hashing)
- Binary data or file contents

Store a reference key in the payload if the full data must be retrievable; keep the payload bounded.

## Consumer/Enricher Responsibilities

The consumer is a **separate process** from the producer. It must be independently deployable and scalable. Do not merge producer and consumer into the same function or class.

### Pull Consumer Loop

```python
sub = await js.pull_subscribe("reports.requests.>", durable="report-enricher")

while True:
    msgs = await sub.fetch(batch=10, timeout=5.0)
    for msg in msgs:
        try:
            await process_message(msg)
        except Exception:
            await msg.nak()
```

### Validation

Reject messages where `payload_version` is unrecognised. Log the rejection with the received version and the message subject. Do not attempt to process unknown schema versions.

```python
if payload.get("payload_version") not in SUPPORTED_VERSIONS:
    logger.error("Unknown payload_version %s — routing to DLQ via nack",
                 payload.get("payload_version"))
    await msg.nak()
    return
```

### Cleaning

Strip any residual PII fields before enrichment:
- Remove raw IP addresses (keep the hash if present).
- Remove any fields that are not part of the defined payload schema.

### Enrichment

Compute derived fields the producer cannot know at publish time:

```python
def enrich(payload: dict) -> dict:
    rt_ms = payload.get("response_time_ms", 0)
    status = payload.get("response_status", 0)

    if rt_ms < 200:
        response_time_class = "fast"
    elif rt_ms <= 2000:
        response_time_class = "slow"
    else:
        response_time_class = "timeout"

    if status == 0:
        error_category = "none"
    elif 400 <= status < 500:
        error_category = "client_error"
    elif status >= 500:
        error_category = "server_error"
    else:
        error_category = "none"

    return {
        **payload,
        "response_time_class": response_time_class,
        "error_category": error_category,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }
```

### Ack After Insert

**Ack the NATS message only after successful MongoDB insertion.** If MongoDB insertion fails, nack the message without immediate redelivery and let `max_deliver` handle retries before routing to the DLQ.

```python
try:
    await repo.insert(enriched_doc)
    await msg.ack()
except PyMongoError as exc:
    logger.error("MongoDB insert failed: %s", exc)
    await msg.nak(delay=5)   # back off before redelivery
```

Never ack before the write confirms — acking signals durable commitment and the message will not be redelivered.

## MongoDB Insertion

### Collection Naming

Use the weekly-bucketed collection pattern from `context/stacks/mongo.md`. Reference the `weekly_collection_name()` helper from `examples/canonical-storage/mongo-weekly-reporting-example.md` rather than duplicating it.

```python
collection_name = weekly_collection_name(enriched_doc["published_at"])
# e.g. "request_logs_2026_w12"
```

### Enriched Document Shape

The document must include all producer fields plus all enrichment fields. `payload_version` must be preserved. Do not store raw NATS message metadata (sequence number, reply subject, headers).

```json
{
  "payload_version": 1,
  "tenant_id": "acme",
  "report_id": "daily-signups",
  "correlation_id": "req-abc-123",
  "published_at": "2026-03-10T14:22:00Z",
  "request_method": "POST",
  "request_path": "/api/reports",
  "response_status": 200,
  "response_time_ms": 142,
  "source_ip_hash": "sha256:abcd1234",
  "response_time_class": "fast",
  "error_category": "none",
  "enriched_at": "2026-03-10T14:22:01Z"
}
```

## Stream and Consumer Configuration

| Field | Value |
|---|---|
| Stream name | `REPORT_REQUESTS` |
| Subject filter | `reports.requests.>` |
| Retention | `WorkQueuePolicy` (delete after ack) or `LimitsPolicy` with an appropriate window |
| Consumer name | `report-enricher` (durable) |
| Ack policy | `AckExplicit` |
| Ack wait | `30s` |
| Max deliver | `5` |
| DLQ stream | `REPORT_REQUESTS_DLQ` |
| DLQ subject | `$JS.EVENT.ADVISORY.CONSUMER.MAX_DELIVERIES.>` |

## Dead Letter Queue

After `max_deliver` failures, NATS publishes an advisory to:
```
$JS.EVENT.ADVISORY.CONSUMER.MAX_DELIVERIES.REPORT_REQUESTS.report-enricher
```

The `REPORT_REQUESTS_DLQ` stream captures these advisories. Operators inspect failed messages from the DLQ stream to diagnose root causes.

To replay a message after fixing the underlying issue:
1. Identify the original message by `correlation_id` and `published_at` from the advisory payload.
2. Reconstruct or retrieve the original payload.
3. Re-publish to the original subject to trigger the consumer pipeline again.

Do not replay by re-publishing directly from the DLQ advisory — the advisory contains metadata about the failure, not the original payload.

## Change Surfaces To Watch

- **Ack/nack ordering**: any code change that moves the MongoDB insert after the ack introduces data loss risk. The ack must always come last.
- **Payload version handling**: adding a new payload version requires updating `SUPPORTED_VERSIONS` in the consumer before the producer starts publishing new versions.
- **Collection naming**: changes to the weekly bucketing helper must be applied consistently across write and read paths.
- **Consumer configuration**: changing `max_deliver` on a live durable consumer requires deleting and recreating the consumer. Plan this carefully.
- **Producer/consumer separation**: resist the temptation to inline enrichment logic in the producer. The separation is load-bearing — producer and consumer scale independently.

## Testing Expectations

- Run `nats-server -js` and `mongo:7` in `docker-compose.test.yml` for integration tests.
- Use a short-lived test stream (1 hour retention or 1000-message limit); purge in teardown.
- Prove the full pipeline: publish one message → consumer processes it → assert MongoDB document exists with expected `response_time_class` and `error_category`.
- Prove the DLQ path: publish a message with an unknown `payload_version` → consumer nacks → assert the advisory appears in `REPORT_REQUESTS_DLQ` after `max_deliver` attempts.
- Do not mock the MongoDB client or the NATS connection for pipeline integration tests.

## Common Assistant Mistakes

- Acking the NATS message before the MongoDB write confirms (data loss on crash).
- Putting producer and consumer logic in the same function (breaks independent scaling).
- Not capping payload size — NATS has a default max payload of 1 MB.
- Using core NATS pub-sub instead of JetStream (no durability, no ack, no DLQ).
- Duplicating the `weekly_collection_name()` helper instead of importing it from the shared module.
- Enriching fields that the producer already knew at publish time — enrichment is for derived fields only.
