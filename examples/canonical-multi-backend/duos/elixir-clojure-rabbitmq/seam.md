# Seam: Elixir + Clojure via RabbitMQ (Broker — Work Queue)

## Purpose

This example demonstrates the RabbitMQ broker seam between a Clojure producer (domain event enrichment) and an Elixir consumer (Broadway-based work queue). The Clojure service publishes enriched domain task events to a RabbitMQ topic exchange; the Elixir service consumes them as a work queue — exactly one worker handles each message.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

This duo fills two gaps simultaneously:
- First canonical RabbitMQ broker seam example in this repo
- First canonical Elixir + Clojure example

## Seam Type

**Broker (async, decoupled, work queue)** — Clojure publishes; Elixir consumes.

## Why RabbitMQ (Not NATS, Not Kafka)

**Work queue semantics**: each enriched task event must be handled by exactly one worker in the Elixir pool, not broadcast to all consumers. RabbitMQ round-robins messages to competing consumers on the same queue. NATS JetStream also supports work queue streams, but RabbitMQ's native work queue model (with prefetch_count) is more operationally direct for this use case.

**Broadway + broadway_rabbitmq**: Elixir's Broadway library provides first-class AMQP work-queue integration — prefetch control, manual ack, DLX-aware failure handling (`on_failure: :reject_and_requeue_once`), and concurrent processor stages. This is the idiomatic Elixir pattern for consuming from an AMQP queue.

**Langohr for Clojure**: Langohr is the mature, idiomatic AMQP client for Clojure — direct AMQP protocol, no abstraction overhead, well-suited to the Kit/tools-deps ecosystem.

**Topic exchange for future flexibility**: although this example routes `domain.tasks.*` to a single queue, the topic exchange allows routing different task types to different queues in the future (e.g., `domain.tasks.billing.*` → one queue, `domain.tasks.shipping.*` → another) without changing the producer.

**Not Kafka**: Kafka is the right choice when multiple independent consumer groups need to read the same events at different offsets (replay), or when volume requires partition scaling. Here, the task distribution model (consumed-once, work queue) is a poor fit for Kafka's log semantics.

**Not NATS**: NATS JetStream work queue streams work, but NATS has no per-message routing concept — all messages go to a single stream subject. The topic exchange routing key pattern is what makes RabbitMQ the natural fit when content-based routing may be needed.

## Exchange / Queue / Binding Topology

```
[Clojure producer]
        |
        | publish routing_key="domain.tasks.created"
        v
  Exchange: "domain-events"  (type: topic, durable)
        |
        | binding: "domain.tasks.*"
        v
  Queue: "domain.tasks.enriched"  (durable, x-dead-letter-exchange="domain-events.dlx")
        |
        | push delivery (prefetch_count=10)
        v
  [Elixir Broadway consumer pool]
        |
        | on reject (requeue=false)
        v
  Exchange: "domain-events.dlx"  (type: direct, durable)
        |
        | routing_key="domain.tasks.failed"
        v
  Queue: "domain.tasks.dlq"  (durable)
```

- The binding pattern `domain.tasks.*` matches one routing key segment after `domain.tasks.` — e.g., `domain.tasks.created`, `domain.tasks.updated`, `domain.tasks.enriched`.
- To route a subset of task types to a different queue, add another binding on the same exchange (no producer change needed).
- The DLX (`domain-events.dlx`) is a direct exchange. Messages rejected by Elixir are routed to `domain.tasks.dlq` for inspection and replay.

## Dead Letter Exchange Pattern

The DLX pattern is declared on the main queue at startup (in `ElixirSide.QueueSetup`):

```elixir
AMQP.Queue.declare(channel, "domain.tasks.enriched",
  durable: true,
  arguments: [
    {"x-dead-letter-exchange", :longstr, "domain-events.dlx"},
    {"x-dead-letter-routing-key", :longstr, "domain.tasks.failed"},
  ]
)
```

This means: if a message is rejected (without requeue), times out, or exceeds max-length, RabbitMQ automatically routes it to `domain-events.dlx` with routing key `domain.tasks.failed`, which lands in `domain.tasks.dlq`.

Broadway's `on_failure: :reject_and_requeue_once` requeues once on first failure, then rejects without requeue on the second — triggering the DLX route. This prevents infinite retry loops while giving transient failures one retry.

## Why Clojure and Elixir Don't Depend on Each Other

Both `elixir-service` and `clojure-service` depend only on `rabbitmq` (condition: service_healthy), not on each other. This is correct for a broker seam — the producer and consumer are fully independent:

- The consumer starts and waits for messages; the producer can start before or after.
- If the producer restarts, the consumer continues processing messages already in the queue.
- If the consumer restarts, the broker holds messages until the consumer reconnects (at-least-once delivery with `durable=true` queue and `persistent=true` messages).

## How to Run

```bash
cd examples/canonical-multi-backend/duos/elixir-clojure-rabbitmq
docker compose up --build
```

Expected startup sequence:
1. RabbitMQ starts and passes its healthcheck (`rabbitmq-diagnostics ping`).
2. `elixir-service` connects, runs `ElixirSide.QueueSetup.run/0` (declares exchange, DLX, queues, bindings), then Broadway starts consuming.
3. `clojure-service` connects, declares the topic exchange (idempotent), publishes one demo event to `domain.tasks.created`, then starts the health endpoint.
4. Elixir receives the message and logs it.

## What to Observe

**Clojure log:**
```
published domain.tasks.created correlation_id=req-demo-001 entity_id=task-001
health endpoint listening on port 8180
```

**Elixir log:**
```
received task event_type=task.enriched entity_id=task-001 tenant_id=demo correlation_id=req-demo-001
```

**RabbitMQ management UI** — open `http://localhost:15672` (guest/guest):
- **Exchanges** tab: `domain-events` (topic, durable) and `domain-events.dlx` (direct, durable) are listed.
- **Queues** tab: `domain.tasks.enriched` shows 0 messages ready (consumed), 0 unacked (acked). `domain.tasks.dlq` shows 0 (no failures).
- **Bindings** on `domain-events`: `domain.tasks.*` → `domain.tasks.enriched`.

**Health endpoints:**
```bash
curl http://localhost:4000/healthz   # {"status":"ok"}
curl http://localhost:8180/healthz   # ok
```

## Scaling Notes

**Adding Elixir workers**: increase `processors: [default: [concurrency: N]]` in `ElixirSide.Consumer`. RabbitMQ distributes messages round-robin across all active consumers on `domain.tasks.enriched` — each message goes to exactly one consumer.

**Adding a second consumer pool** (e.g., a Python worker): declare a second queue, bind it to `domain-events` with a different routing key pattern (e.g., `domain.tasks.billing.*`), and connect the Python consumer to that queue. No change to the Clojure producer is needed.

**prefetch_count**: set to 10, meaning each Broadway producer stage holds at most 10 unacked messages at a time. Tune this based on per-message processing time — lower for slow processing, higher for fast processing.

## Schema Evolution

When the event shape changes materially, increment `payload_version`. The Elixir consumer pattern-matches on this field and rejects (with warning) any version it does not handle, routing the message to the DLQ rather than crashing or silently misprocessing. This gives the operator time to inspect and replay after deploying a consumer that handles the new version.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-elixir-clojure.md`
- `context/stacks/elixir-phoenix.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/stacks/rabbitmq.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/doctrine/broker-selection.md`
