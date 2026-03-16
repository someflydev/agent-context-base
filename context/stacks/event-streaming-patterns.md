# Event Streaming Patterns

Patterns for coordinating repo stages through durable events, subjects, or queues, regardless of which broker is in use. For the broker choice itself, see `context/doctrine/broker-selection.md` — this doc covers patterns that apply once the broker is chosen.

## Broker Options

| Broker | When to reach for it |
|---|---|
| NATS JetStream | Lightweight intra-cluster bus, single binary, NATS already in use |
| Kafka | High volume (> 1M msg/day), cross-team schema contracts, JVM producer (Clojure/Scala) |
| Redis Streams | Job queue on existing Redis, no separate broker service needed |

Full stack docs: `context/stacks/nats-jetstream.md`, `context/stacks/kafka.md`, `context/stacks/redis.md`.

## Typical Repo Surface

- **Scheduler or trigger publisher**: a function or cron job that publishes an event to kick off a sync stage. Example: publish a `sync.requested` event on a timer; the event contains the `tenant_id`, `entity_id`, and a `correlation_id` for tracing the downstream chain.

- **Event handler / worker**: subscribes to an input subject/topic/stream; processes the message and optionally publishes a completion or failure event. The handler must be idempotent — at-least-once delivery means it can receive the same message more than once.

- **DLQ consumer**: subscribes to the dead-letter subject/topic/stream; logs failures, triggers alerting, optionally republishes for manual retry. Never auto-retry from the DLQ — require human intervention.

- **Health probe for broker connectivity**: each service exposes `/healthz` that checks broker connectivity, not just process liveness. A service that cannot reach its broker should be considered unhealthy.

## Event Schema Invariants

These apply regardless of broker. Every event must include:

| Field | Purpose |
|---|---|
| `payload_version` | Integer; increments on schema changes; consumers pattern-match on this field |
| `correlation_id` | Propagated from the triggering request or job; used for distributed tracing |
| `published_at` | ISO 8601 UTC timestamp set by the producer, not the broker |
| `entity_id` (or equivalent) | The primary business entity this event concerns |

Anti-patterns:
- Putting raw document bodies in events — pass a reference ID; let the consumer fetch.
- Omitting `payload_version` — impossible to evolve the schema without breaking consumers.
- Treating topics/subjects as action queues — use event noun names (`order.created`), not verb names (`process-order`).

## Idempotency and Duplicate Delivery

All three brokers provide at-least-once delivery, not exactly-once by default. Consumer handlers must be idempotent:

- Use `correlation_id` or `entity_id` as an idempotency key.
- Check for prior processing before doing work (e.g., database upsert with conflict handling).
- If the handler is not naturally idempotent, add an idempotency store: `SET {key} 1 NX EX {ttl}` in Redis is a reliable pattern.

Idempotency key pattern:
```
{consumer_group}:{entity_id}:{payload_version}:{published_at_date}
```

Changing the idempotency key shape invalidates existing idempotency records — plan migrations carefully.

## Dead Letter Handling

Send a message to the DLQ when:
- Schema version is unsupported by the current handler.
- Entity not found after retries (the upstream data is missing).
- Business rule definitively rejects the event.
- Max retry count exceeded.

DLQ event payload must include: original message, error message, `retry_count`, `failed_at` timestamp.

Per-broker DLQ naming:
| Broker | DLQ location |
|---|---|
| NATS JetStream | Publish to `{original_subject}.dlq` |
| Kafka | Produce to `{original_topic}.dlq` |
| Redis Streams | XADD to `{stream_key}:dlq` |

A DLQ monitor service should alert on any message in the DLQ within N minutes. Never silently discard failed messages.

## Change Surfaces To Watch

- **Event subject/topic/stream naming**: changes break consumers silently if not versioned. Treat the subject/topic prefix as a stable API — the same as a REST endpoint path.
- **`payload_version` field**: bump it on every schema change; consumers must handle the old version until all are migrated.
- **Idempotency key shape**: changes invalidate existing idempotency records and may cause reprocessing or duplicate suppression failures.
- **Consumer group ID**: changing it resets offsets/positions and may cause reprocessing or gaps in coverage.
- **Checkpoint movement**: move the consumer checkpoint (ack/commit/xack) only after successful processing is confirmed, not before. Acking before processing is confirmed causes data loss on crash.
- **Payload size and reference strategy**: events must not carry raw document bodies — pass reference IDs. Max payload size matters especially for NATS (1 MB default limit).

## Testing Expectations

- Prove one event-driven happy path end to end against a real broker in docker-compose.
- Prove duplicate delivery handling: publish the same message twice, assert the consumer processes it once (or handles it idempotently without side effects).
- Prove DLQ delivery for a malformed message — wrong `payload_version` or missing required field.
- Keep large raw payload bodies out of event messages; pass references instead.
- Do not mock the broker client in integration tests — use the real broker. Ack and offset commit behavior cannot be meaningfully tested with mocks.

## Common Assistant Mistakes

- Publishing framework-centric event names (`request.received`, `response.sent`) instead of sync-stage domain names (`order.created`, `sync.requested`).
- Putting raw document bodies directly on the bus — always pass a reference ID.
- Assuming ordered delivery across unrelated sources — ordering is per-subject (NATS), per-partition (Kafka), or per-stream (Redis Streams), not global.
- Omitting `payload_version` because the schema "won't change" — it always will.
- Not handling the DLQ path in the initial implementation — add it before the first production deployment.

## Related

- context/doctrine/broker-selection.md
- context/stacks/nats-jetstream.md
- context/stacks/kafka.md
- context/stacks/redis.md (Redis Streams section)
- context/stacks/coordination-seam-patterns.md (broker seam implementation for multi-backend)
