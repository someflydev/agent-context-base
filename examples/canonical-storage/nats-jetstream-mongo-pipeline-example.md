# NATS JetStream + MongoDB Pipeline Example

**Verification level: structure-verified**
Harness: none (recommended follow-on: add `docker-compose.test.yml` with `nats-server -js` + `mongo:7` for smoke-verified coverage)
Last verified by: `verification/examples/data/test_storage_examples.py`

This document covers the full capture-enrich-persist pipeline:

```
Producer → NATS JetStream (REPORT_REQUESTS stream) → Consumer/Enricher → MongoDB (weekly-bucketed collection)
```

The producer and consumer are **separate processes** with separate responsibilities. Do not merge them.

---

## Stream and Consumer Configuration

| Field | Value |
|---|---|
| Stream name | `REPORT_REQUESTS` |
| Subject filter | `reports.requests.>` |
| Retention | `WorkQueuePolicy` (messages deleted after ack) |
| Consumer name | `report-enricher` (durable) |
| Ack policy | `AckExplicit` |
| Ack wait | `30s` |
| Max deliver | `5` |
| DLQ stream | `REPORT_REQUESTS_DLQ` |
| DLQ subject | `$JS.EVENT.ADVISORY.CONSUMER.MAX_DELIVERIES.REPORT_REQUESTS.report-enricher` |

---

## Producer

### Bounded Payload

The producer constructs a bounded payload from the raw request/response. It never stores raw HTTP bodies, unbounded arrays, or PII fields that do not belong in the reporting layer.

**Subject naming:** `reports.requests.<tenant_id>.<report_id>`

```
reports.requests.acme.daily-signups
reports.requests.globex.weekly-revenue
```

**Required payload fields:**

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
  "source_ip_hash": "sha256:abcd1234ef567890"
}
```

**What NOT to put in the payload:**
- Raw HTTP request or response body (can be megabytes; hits the 1 MB NATS max payload limit)
- Unbounded arrays (query result rows, item lists)
- PII fields: raw IP addresses, email addresses, user names — hash or omit
- Binary data or file contents

### Publish Snippet (Python, nats library)

```python
import asyncio
import json
import nats

async def publish_request_event(
    nc: nats.aio.client.Client,
    payload: dict,
) -> None:
    js = nc.jetstream()
    subject = f"reports.requests.{payload['tenant_id']}.{payload['report_id']}"
    await js.publish(subject, json.dumps(payload).encode())
    # The producer does not wait for consumer confirmation.
    # The stream provides durability — once the broker acks the publish,
    # the message is durable regardless of consumer availability.
```

---

## Consumer / Enricher

The consumer is a **separate process** from the producer. It runs independently and scales independently. Do not inline enrichment in the producer.

### Durable Pull Consumer Setup

```python
import nats

async def setup_consumer(js) -> nats.js.client.PushSubscription:
    # Create the stream if it does not already exist
    await js.add_stream(
        name="REPORT_REQUESTS",
        subjects=["reports.requests.>"],
        retention="workqueue",
    )
    # Durable pull consumer
    return await js.pull_subscribe(
        subject="reports.requests.>",
        durable="report-enricher",
        config=nats.js.api.ConsumerConfig(
            ack_policy=nats.js.api.AckPolicy.EXPLICIT,
            ack_wait=30,
            max_deliver=5,
        ),
    )
```

### Fetch-Process-Ack Loop

```python
async def run_consumer_loop(sub) -> None:
    while True:
        try:
            msgs = await sub.fetch(batch=10, timeout=5.0)
        except nats.errors.TimeoutError:
            continue  # no messages; keep polling

        for msg in msgs:
            payload = json.loads(msg.data)
            try:
                await process_message(msg, payload)
            except Exception as exc:
                # Nack without immediate redelivery — let max_deliver handle retries.
                await msg.nak(delay=5)
                logger.error("Processing failed: %s", exc)
```

### Validation

```python
SUPPORTED_VERSIONS = {1}

def validate(payload: dict) -> None:
    version = payload.get("payload_version")
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(f"Unknown payload_version: {version!r}")
```

Reject messages with unknown `payload_version`. Log the rejection. Do not attempt to process unknown schema versions.

### Cleaning

Strip any residual PII fields before enrichment:

```python
PII_FIELDS = {"raw_ip", "email", "user_name"}

def clean(payload: dict) -> dict:
    return {k: v for k, v in payload.items() if k not in PII_FIELDS}
```

### Enrichment

Compute derived fields the producer cannot know at publish time:

```python
from datetime import datetime, timezone

def enrich(payload: dict) -> dict:
    rt_ms = payload.get("response_time_ms") or 0
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

**Enrichment fields:**

| Field | Values | Derivation |
|---|---|---|
| `response_time_class` | `fast` \| `slow` \| `timeout` | `response_time_ms` thresholds: <200ms, 200–2000ms, >2000ms |
| `error_category` | `none` \| `client_error` \| `server_error` | HTTP status: 4xx → client, 5xx → server, else none |
| `enriched_at` | ISO 8601 UTC | Consumer-side timestamp, not producer-side |

### Handle MongoDB Write Failure

```python
from pymongo.errors import PyMongoError

async def process_message(msg, payload: dict) -> None:
    validate(payload)
    cleaned = clean(payload)
    enriched = enrich(cleaned)

    try:
        await insert_to_mongo(enriched)
        # ACK only after successful MongoDB insertion
        await msg.ack()
    except PyMongoError as exc:
        logger.error("MongoDB insert failed for correlation_id=%s: %s",
                     payload.get("correlation_id"), exc)
        # Nack — let max_deliver handle retries before routing to DLQ
        await msg.nak(delay=5)
```

**Critical rule:** Ack the NATS message only after `insert_to_mongo()` confirms. Acking before the write creates data loss on crash.

---

## MongoDB Insertion

### Collection Naming

Use the weekly-bucketed collection naming pattern from `context/stacks/mongo.md` and the `weekly_collection_name()` helper from `examples/canonical-storage/mongo-weekly-reporting-example.md`. Do not duplicate the helper.

```python
from app.db.mongo_helpers import weekly_collection_name

collection_name = weekly_collection_name(enriched_doc["published_at"])
# e.g. "request_logs_2026_w12"
```

### Enriched Document Shape

The enriched document must include all producer fields plus all enrichment fields. `payload_version` is preserved. Raw NATS message metadata (sequence, reply subject, headers) is not stored.

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
  "source_ip_hash": "sha256:abcd1234ef567890",
  "response_time_class": "fast",
  "error_category": "none",
  "enriched_at": "2026-03-10T14:22:01Z"
}
```

### Insert Call

```python
async def insert_to_mongo(enriched: dict) -> None:
    collection_name = weekly_collection_name(enriched["published_at"])
    collection = db[collection_name]
    result = await collection.insert_one(enriched)
    if not result.inserted_id:
        raise RuntimeError("insert_one returned no inserted_id")
```

---

## Dead Letter Queue

### What the DLQ Looks Like

After `max_deliver` (5) failures, NATS publishes an advisory to:
```
$JS.EVENT.ADVISORY.CONSUMER.MAX_DELIVERIES.REPORT_REQUESTS.report-enricher
```

The `REPORT_REQUESTS_DLQ` stream captures these advisories. Each advisory contains metadata about the failed message: stream name, consumer name, stream sequence, delivery count.

### Inspecting Failed Messages

```bash
# List messages in the DLQ stream using the NATS CLI
nats stream view REPORT_REQUESTS_DLQ
```

The advisory payload does not contain the original message body. Use the stream sequence number from the advisory to look up the original message in the source stream (if still within the retention window).

### Replaying a Failed Message

1. Identify the original message from the advisory (`stream_seq` field).
2. Retrieve the original payload from your raw archive or re-construct it.
3. Re-publish to the original subject to trigger the consumer pipeline again.
4. Verify the message is consumed and the MongoDB document is created.

Do not replay by forwarding the advisory itself — it is a metadata event, not the original payload.

---

## Integration Test Coverage

The recommended integration test proves:

1. **Happy path**: publish one well-formed message → consumer processes it → MongoDB document exists with expected `response_time_class` and `error_category`.
2. **DLQ path**: publish a message with an unknown `payload_version` → consumer nacks → after `max_deliver` attempts, the advisory appears in `REPORT_REQUESTS_DLQ`.

Test infrastructure in `docker-compose.test.yml`:
```yaml
services:
  nats-test:
    image: nats:latest
    command: "-js"
    ports:
      - "14222:4222"

  mongo-test:
    image: mongo:7
    ports:
      - "27018:27017"
    volumes:
      - mongo-test-data:/data/db

volumes:
  mongo-test-data:
```

A live docker-compose harness with both services would provide **smoke-verified** coverage. That is the recommended follow-on step from the current structure-verified baseline.
