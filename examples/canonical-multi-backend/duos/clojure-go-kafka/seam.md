# Seam: Clojure + Go via Kafka (Broker)

## Purpose

This example demonstrates the broker seam between a Clojure service that produces enriched domain events and a Go service that consumes them as a worker pool. The seam is Kafka with KRaft (no ZooKeeper), bitnami/kafka:3.7.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**Broker (async, decoupled)** — Clojure produces; Go consumes.

## Why Kafka (Not NATS) for This Seam

Kafka is the right choice here because:

- **Cross-team schema contracts**: the event schema is shared between Clojure (producer team) and Go (worker team). Kafka's topic contract, with `payload_version` as a consumer guard, provides a stable handoff point without requiring runtime negotiation.
- **Independent consumer group offset tracking**: Go workers track their own offsets independently. Multiple Go worker instances share the `go-risk-workers` group ID; Kafka distributes partitions among them automatically. No consumer knows about other consumers.
- **Long-term retention for replay**: Kafka retains messages for the configured retention period. If the Go worker pool needs to reprocess events (e.g., after a bug fix), it can reset its consumer group offsets to replay from an earlier point.

For small volumes or simpler fan-out without the above requirements, NATS JetStream is the lighter alternative. See `context/stacks/nats-jetstream.md` and `context/doctrine/broker-selection.md`.

## Topic and Partition Key

Topic: `domain.orders.enriched`
Partition key: `tenant_id`

All events for the same tenant land in the same partition, preserving order within a tenant. Go workers assigned to that partition see tenant events in order.

## Event Schema

```json
{
  "payload_version": 1,
  "correlation_id": "req-demo-001",
  "published_at": "2026-03-16T12:00:00.000Z",
  "tenant_id": "demo",
  "event_type": "order.risk_scored",
  "entity_id": "ord-001",
  "data": {
    "risk_score": 0.12,
    "risk_tier": "low",
    "rule_version": "2026-Q1",
    "triggered_rules": ["velocity_check"]
  }
}
```

Field notes:
- `payload_version`: Go consumers check this field first. Unknown versions are logged as DLQ candidates and the record is committed (partition does not stall).
- `correlation_id`: propagated through all downstream processing for distributed tracing.
- `triggered_rules`: bounded array — at most ~20 entries. Do not embed large nested objects.

## Consumer Group Semantics

Multiple Go worker instances can run with the same `GROUP_ID=go-risk-workers`. Kafka assigns partitions among them. When a worker dies, Kafka triggers a rebalance and redistributes its partitions to remaining workers. No Go code needs to manage this — it is handled by the Kafka consumer group protocol and franz-go.

Clojure does not know or care how many Go workers are running. The broker seam means the producer has no dependency on the consumer.

## Why Clojure and Go Don't Have Mutual `depends_on`

In this example, `clojure-service` and `go-service` both `depends_on: kafka` only. Neither depends on the other. This is the correct model for a broker seam:

- Clojure can produce events to Kafka before Go is consuming. Kafka retains the messages — Go will process them when it starts.
- Go can start consuming from Kafka before Clojure has produced anything. Go will simply wait for new messages.
- The ordering of producer and consumer startup is irrelevant. The broker is the durable intermediary.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/clojure-go-kafka
docker compose up --build
```

Expected sequence:
1. Kafka starts, passes its healthcheck (`kafka-topics.sh --list`).
2. `clojure-service` starts (JVM startup takes ~30s), connects to Kafka, publishes the demo event to `domain.orders.enriched`, then starts the http-kit health endpoint on port 8180.
3. `go-service` starts, connects to Kafka as consumer group `go-risk-workers`, subscribes to `domain.orders.enriched`, starts the health endpoint on port 8080.

## What to Observe

- Clojure log: `publishing demo event to domain.orders.enriched` followed by `healthz listening on :8180`
- Go log: `received event_type=order.risk_scored entity_id=ord-001 risk_score=0.12 risk_tier=low correlation_id=req-demo-001`
- Health endpoints: `curl http://localhost:8180/healthz` and `curl http://localhost:8080/healthz` both return `{"status":"ok"}`

## Inspecting Consumer Group Offsets

From inside the kafka container:

```bash
docker compose exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group go-risk-workers \
  --describe
```

Output shows partition assignments, current offset, log-end offset, and consumer lag per partition.

## Schema Evolution

The `payload_version` field is the evolution guard:

- **Adding fields to the JSON payload**: backward-compatible. Go consumers ignore unknown fields via `json.Unmarshal`. Clojure producers add the new field without changing `payload_version`.
- **Removing or renaming fields that Go reads**: breaking change. Increment `payload_version` to 2. Go consumers must handle both versions before the old version is removed from production traffic.
- **Changing field types**: always breaking. Treat as a new version.

For cross-team Avro schemas with registry enforcement, see the schema strategy section in `context/stacks/kafka.md`.

## Related

- `context/stacks/duo-clojure-go.md` — full division of labor and when to use this pair
- `context/stacks/kafka.md` — Kafka stack doc: topics, partitions, consumer patterns, DLQ
- `context/stacks/coordination-seam-patterns.md` — Kafka broker seam snippet
- `context/doctrine/broker-selection.md` — NATS vs Kafka vs Redis Streams decision
