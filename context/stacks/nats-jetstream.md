# NATS JetStream

Use this pack when the repo adds a durable, subject-routed message streaming layer for lightweight event pipelines. JetStream is NATS with persistence — it adds at-least-once delivery, durable consumers, and ack semantics on top of the core NATS pub-sub fabric.

## When NATS JetStream Is the Right Choice

- Lightweight durable message bus without the operational overhead of Kafka (no ZooKeeper, no partition rebalancing, single binary).
- Subject-based routing where consumers filter by subject pattern using wildcards (`*` matches one token, `>` matches any remaining tokens).
- Pipelines where at-least-once delivery with explicit consumer ack is sufficient.
- Small-to-medium message volumes where horizontal Kafka partition scaling is unnecessary.
- Repos that need a real broker for integration tests without standing up a Kafka cluster.

## When NATS JetStream Is NOT the Right Choice

- Very high throughput requiring horizontal partition scaling — use Kafka.
- When a schema registry is needed for cross-team consumer compatibility — use Kafka with Avro or Protobuf.
- When ordering guarantees must span multiple subjects simultaneously — NATS ordering is per-subject.
- When the consumer ecosystem expects Kafka client libraries specifically.

## Typical Repo Surface

- `app/messaging/nats_client.py` — connection setup, stream and consumer configuration
- `app/messaging/producer.py` — message construction and publish logic
- `app/messaging/consumer.py` — pull consumer fetch loop, ack/nack handling
- `etc/nats/jetstream.conf` — optional server config file for stream definitions
- `tests/integration/test_nats_pipeline.py` — publish one message, consume and assert
- `docker-compose.test.yml` — `nats` service with `-js` flag enabled

## Core Concepts

### Streams

A stream is durable storage for all messages matching a subject pattern. Streams persist messages according to a retention policy (limits-based or work-queue).

```python
js = nc.jetstream()
await js.add_stream(name="REPORT_REQUESTS", subjects=["reports.requests.>"])
```

### Subjects

Dot-separated routing keys. Subject naming convention:

```
<domain>.<event_type>.<tenant_id>.<entity_id>
```

Example: `reports.requests.acme.daily-signups`

Rules:
- Use dots as separators, not slashes or underscores.
- Keep the prefix stable (`reports.requests`); terminal segments can be wildcarded.
- Never treat subjects like REST URLs — they are routing keys, not resource paths.

### Consumers

Durable pull consumers fetch messages in controlled batches. Key configuration fields:

| Field | Recommended value | Why |
|---|---|---|
| `durable_name` | `report-enricher` | Survives server restart |
| `ack_policy` | `AckExplicit` | Each message acked individually |
| `ack_wait` | `30s` | Time before unacked message is redelivered |
| `max_deliver` | `5` | After 5 failures, routes to advisory DLQ |
| `filter_subject` | `reports.requests.>` | Scope the consumer to its subject prefix |

### Ack and Nack Semantics

- **Ack**: signals successful processing. The message is removed from the work queue (for `WorkQueuePolicy` streams).
- **Nack**: signals failure. The message is redelivered after `ack_wait`. If `max_deliver` is exceeded, the message is published to the advisory dead-letter subject.
- **In-progress**: call `.in_progress()` to extend `ack_wait` during long processing.

Never ack before processing is complete — acking signals durable commitment to the broker.

### Dead Letter Queue

Messages that exceed `max_deliver` are published to the JetStream advisory subject:
```
$JS.EVENT.ADVISORY.CONSUMER.MAX_DELIVERIES.<STREAM>.<CONSUMER>
```

Create a `REPORT_REQUESTS_DLQ` stream to capture these advisories. Inspect and replay failed messages from the DLQ after fixing the underlying issue.

## Message Payload Shape

Always include these fields in every published payload:

```json
{
  "payload_version": 1,
  "tenant_id": "acme",
  "correlation_id": "req-abc-123",
  "published_at": "2026-03-10T14:22:00Z",
  ...
}
```

Rules:
- `payload_version`: consumers reject or adapt based on this field. Increment it when the shape changes materially.
- `published_at`: ISO 8601 UTC timestamp set by the producer, not the broker.
- `tenant_id` and `correlation_id`: enable consumer-side deduplication and downstream tracing.
- Cap message size. NATS has a default max payload of 1 MB. Do not put raw HTTP response bodies, unbounded arrays, or binary blobs in the payload. Store a reference key instead and retrieve from object storage.

## Docker Dev Setup

```yaml
services:
  nats:
    image: nats:latest
    command: "-js"
    ports:
      - "4222:4222"   # Client port
      - "8222:8222"   # HTTP monitoring
```

For integration tests, use a dedicated test stream with a short retention window (e.g. 1 hour or 1000 messages max). Always purge or delete the test stream in teardown.

## Change Surfaces To Watch

- **Subject naming**: changing a subject prefix breaks existing durable consumers. Treat subject prefixes as a stable API.
- **Consumer configuration**: changing `max_deliver` or `ack_wait` on a live consumer requires deleting and recreating it. Plan consumer config changes carefully.
- **Payload version handling**: consumers must reject messages with unknown `payload_version` values rather than silently processing them with the wrong field map.
- **Stream retention policy**: changing from `LimitsPolicy` to `WorkQueuePolicy` changes when messages are deleted. Test this transition with real data.

## Testing Expectations

- Use the official `nats` Docker image with the `-js` flag for integration tests.
- Create the test stream in test setup; purge or delete it in teardown.
- Prove the full loop: publish one message → pull consumer fetches it → message is acked → assert it no longer appears in the stream.
- Prove the DLQ path: publish a message that will fail enrichment → assert it appears in the DLQ stream after max_deliver attempts.
- Do not use the in-memory NATS server for consumer ack behavior tests — use the real Docker-backed broker.

## Common Assistant Mistakes

- Treating NATS subjects like REST routes (subjects are routing keys, not URLs).
- Not setting `max_deliver` on the consumer (failed messages loop forever).
- Using core NATS pub-sub (no durability) instead of JetStream when durable delivery is required.
- Storing raw large payloads in NATS instead of a reference key pointing to object storage.
- Acking a message before the downstream write (database insert, file write) confirms — this creates data loss on crash.
- Skipping real broker tests for consumer ack and nack behavior; these cannot be meaningfully tested with mocks.
