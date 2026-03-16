# RabbitMQ

Use this pack when the repo adds a message broker with AMQP-native routing — topic exchange pattern bindings, work-queue delivery semantics, and dead-letter exchange support. RabbitMQ is the right broker when task distribution (exactly one worker handles each message), content-based routing by routing key, or AMQP ecosystem conventions (DLX, TTL, priority queues) are the primary requirements.

## When RabbitMQ Is the Right Choice

- **Task distribution**: a message must be delivered to exactly one worker in a pool (work queue semantics; RabbitMQ round-robins messages to competing consumers on the same queue).
- **Content-based routing**: messages need to be routed to different queues based on routing key patterns using a topic exchange (e.g., `*.orders.us` → one queue, `*.orders.eu` → another).
- **Priority queues**: urgent tasks must preempt normal tasks in a queue.
- **Request/reply patterns**: caller publishes to a queue and waits for a response on a reply-to queue (RPC-over-AMQP; use sparingly — prefer gRPC for synchronous calls).
- **AMQP ecosystem integration**: teams with existing RabbitMQ infrastructure or where AMQP client libraries (Langohr, aio-pika, amqp, bunny) are already in use.
- **AMQP workflow conventions already in use**: dead-letter-exchange, TTL, priority — these map directly to RabbitMQ broker configuration.
- **Elixir as producer or consumer**: Broadway's `broadway_rabbitmq` provides first-class work-queue integration with manual ack, prefetch control, and DLX-aware failure handling.

## When RabbitMQ Is NOT the Right Choice

- **High-throughput log-style event streams** where multiple independent consumer groups need replay → use Kafka. RabbitMQ messages are consumed once and deleted; Kafka retains them for offset-based replay.
- **Lightweight subject-routed pub/sub without queue semantics** → use NATS JetStream. NATS subject wildcards are simpler to operate for fan-out use cases.
- **Repo already runs Redis and volume is modest** → use Redis Streams. Adding RabbitMQ for one use case adds infrastructure friction.
- **Fan-out to many consumers where each consumer gets a copy**: fanout exchange works, but NATS subject wildcards are simpler for most fan-out use cases.
- **Cross-team schema contracts requiring Avro or Protobuf with a registry** → use Kafka.
- **Volume requiring partition-level horizontal scaling** → use Kafka.

## Typical Repo Surface

- `app/messaging/rabbitmq_connection.py` — connection setup, exchange/queue/binding declarations
- `app/messaging/publisher.py` — message construction and publish logic (topic exchange)
- `app/messaging/consumer.py` — push consumer loop, prefetch config, manual ack/reject
- `lib/my_app/amqp/consumer.ex` — Broadway pipeline (Elixir), queue declaration, DLX arguments
- `tests/integration/test_rabbitmq_pipeline.py` — publish → consume round-trip; DLQ path
- `docker-compose.test.yml` — `rabbitmq:3.13-management-alpine` service with healthcheck

## Core Concepts

### Exchanges

An exchange receives messages from publishers and routes them to queues based on exchange type and routing key. Exchanges do not store messages — they route them.

**Always declare exchanges as `durable=True`** — non-durable exchanges disappear on broker restart.

### Queues

A queue stores messages until a consumer retrieves and acknowledges them. Key properties:

- `durable=True` — queue survives broker restart
- `x-dead-letter-exchange` — destination for rejected or TTL-expired messages
- `x-dead-letter-routing-key` — routing key used when publishing to the DLX
- `x-message-ttl` — milliseconds before unacknowledged messages are dead-lettered
- `x-max-priority` — enables priority queue semantics (0–255)

### Bindings

A binding links a queue to an exchange with an optional routing key pattern. The exchange uses the binding key to decide which queues receive a message.

### Routing Keys

A routing key is a dot-separated string set by the publisher. Exchanges use it to match against binding patterns. Example: `domain.orders.created`.

## Exchange Types

| Type | Routing logic | Example use |
|---|---|---|
| `direct` | Exact match between routing key and binding key | `order.created` → `order-processor` queue |
| `topic` | Pattern match: `*` matches one word, `#` matches zero or more | `us.orders.*` → `us-order-handler`; `*.orders.#` → `all-orders-monitor` |
| `fanout` | Broadcasts to all bound queues, ignores routing key | `notifications` → email-queue, sms-queue, push-queue |
| `headers` | Routes by message header attributes, not routing key | Rarely needed; use `topic` instead |

**Default for this repo: `topic` exchange** — it gives routing flexibility without committing to exact-match only. A `direct` exchange is a special case of a `topic` exchange with no wildcards.

## Message Schema and Payload Convention

Every RabbitMQ message in this repo must include the following fields in the JSON body:

```json
{
  "payload_version": 1,
  "correlation_id": "req-abc123",
  "published_at": "2026-03-16T10:30:00Z",
  "routing_key": "domain.orders.created",
  "entity_id": "ord-001",
  "tenant_id": "acme",
  "data": { }
}
```

Rules:
- `payload_version`: consumers check this first; unknown versions are rejected with requeue=false, not silently processed.
- `correlation_id`: propagated through all downstream processing for tracing.
- `routing_key` in the body mirrors the AMQP routing key used for publishing — makes the message self-describing.
- `published_at`: ISO 8601 UTC timestamp set by the producer, not the broker.

## Publisher Patterns

Python publisher (`aio-pika`):

```python
# pip install aio-pika
import aio_pika
import json
import asyncio

async def publish_event(amqp_url: str, exchange_name: str, routing_key: str, event: dict) -> None:
    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        message = aio_pika.Message(
            body=json.dumps({
                "payload_version": 1,
                "correlation_id": event.get("correlation_id", ""),
                "published_at": event.get("published_at", ""),
                "routing_key": routing_key,
                **event,
            }).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # survive broker restart
            content_type="application/json",
        )
        await exchange.publish(message, routing_key=routing_key)
```

Clojure publisher (Langohr, `deps.edn: com.novemberain/langohr {:mvn/version "5.4.0"}`):

```clojure
(require '[langohr.core      :as rmq]
         '[langohr.channel   :as lch]
         '[langohr.exchange  :as le]
         '[langohr.basic     :as lb])

(defn publish-event [conn exchange routing-key event]
  (let [ch      (lch/open conn)
        payload (cheshire.core/encode event)]
    (le/declare ch exchange "topic" {:durable true})
    (lb/publish ch exchange routing-key payload
                {:content-type "application/json"
                 :persistent   true
                 :correlation-id (:correlation-id event)})))
```

## Consumer Patterns

### Elixir — Broadway + broadway_rabbitmq (preferred for work queues)

```elixir
# mix.exs deps:
# {:broadway, "~> 1.0"},
# {:broadway_rabbitmq, "~> 0.7"}

defmodule MyApp.OrderConsumer do
  use Broadway

  def start_link(_opts) do
    Broadway.start_link(__MODULE__,
      name: __MODULE__,
      producer: [
        module: {BroadwayRabbitMQ.Producer,
          queue: "order-processor",
          connection: [
            host: System.get_env("RABBITMQ_HOST", "rabbitmq"),
            port: 5672,
            username: System.get_env("RABBITMQ_USER", "guest"),
            password: System.get_env("RABBITMQ_PASS", "guest"),
          ],
          on_failure: :reject_and_requeue_once,  # dead-letter after one retry
          qos: [prefetch_count: 10],
        },
        concurrency: 1,
      ],
      processors: [
        default: [concurrency: 4]
      ]
    )
  end

  @impl true
  def handle_message(_processor, message, _context) do
    event = Jason.decode!(message.data)
    case event["payload_version"] do
      1 -> process_v1(event)
      v -> Broadway.Message.failed(message, "unsupported payload_version: #{v}")
    end
  end

  defp process_v1(event) do
    # business logic
    :ok
  end
end
```

### Python — aio-pika with manual ack

```python
async def consume(amqp_url: str, queue_name: str) -> None:
    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(requeue=False):  # ack on context exit; reject on exception
                    try:
                        event = json.loads(message.body)
                        process_event(event)
                    except Exception:
                        # reject without requeue — message goes to DLX
                        raise
```

Key consumer rules:
- **Always use manual ack** — never `no_ack=True`. Auto-ack sends the ack before processing completes; a crash causes message loss.
- **Always set `prefetch_count`** — without it, one slow consumer holds all messages, starving others.
- **Reject without requeue** (`requeue=False`) on unrecoverable errors — the message routes to the DLX. Requeue only for transient failures.

## Dead Letter Exchanges and Queues

The DLX pattern ensures that rejected, TTL-expired, or max-length-exceeded messages are not silently dropped:

1. **Declare a DLX** (direct or topic exchange, durable):
   ```python
   await channel.declare_exchange("dlx", aio_pika.ExchangeType.DIRECT, durable=True)
   ```

2. **Declare the main queue with DLX arguments**:
   ```python
   queue = await channel.declare_queue(
       "order-processor",
       durable=True,
       arguments={
           "x-dead-letter-exchange": "dlx",
           "x-dead-letter-routing-key": "order-processor.failed",
       }
   )
   ```

3. **Declare the DLQ** and bind it to the DLX:
   ```python
   dlq = await channel.declare_queue("order-processor.dlq", durable=True)
   await dlq.bind("dlx", routing_key="order-processor.failed")
   ```

Pattern: for each main queue `foo`, declare a DLQ `foo.dlq` bound to the DLX.

RabbitMQ automatically adds an `x-death` header to dead-lettered messages containing the original queue, exchange, routing key, reason (`rejected`, `expired`, `maxlen`), and delivery count. Inspect this in DLQ consumers for alerting and replay decisions.

## Local Dev Composition

`rabbitmq:3.13-management-alpine` — includes the management UI at port 15672 (default guest/guest):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # management UI
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s
```

The management UI at `http://localhost:15672` shows live exchange topology, queue depths, consumer counts, and dead-letter routes. Use it during dev to verify binding configuration before writing test assertions.

## Testing Expectations

- Run integration tests against a real RabbitMQ broker (Docker-backed `rabbitmq:3.13-management-alpine`).
- **Prove one publish + consume round-trip** with manual ack — assert the message is removed from the queue after ack.
- **Prove dead-letter delivery**: reject a message without requeue; assert it appears in the DLQ.
- **Prove topic exchange routing**: publish with two different routing keys; assert each lands in the correct queue, not the other.
- **Prove prefetch_count**: publish N > prefetch_count messages; assert at most prefetch_count are in-flight simultaneously.
- Do NOT mock the AMQP client in integration tests — the broker behavior (DLX routing, prefetch, queue durability) is what is tested.
- Keep test queues isolated per test run using a unique queue suffix or dedicated vhost.

## Common Assistant Mistakes

- **Using auto-ack (`no_ack=True`)** — auto-ack sends the ack before processing completes. A crash after ack causes message loss. Always use manual ack.
- **Declaring exchanges and queues without `durable=True`** — they disappear on broker restart.
- **Not declaring the DLX on the main queue at startup** — rejected messages are silently dropped rather than routed to the DLQ.
- **Using a `direct` exchange when a `topic` exchange is needed** — `direct` requires exact routing key match; `topic` gives future routing flexibility at no cost.
- **Hardcoding the connection URL in code** — use `RABBITMQ_URL` or separate `RABBITMQ_HOST` / `RABBITMQ_USER` / `RABBITMQ_PASS` env vars.
- **Not setting `prefetch_count`** — without it, one slow consumer holds all messages, starving all others. Set prefetch to a value that reflects the consumer's processing capacity.
- **Not setting `persistent` delivery mode on published messages** — non-persistent messages are lost if the broker restarts before the consumer acks.

## Related

- `context/doctrine/broker-selection.md` — four-way NATS vs Kafka vs Redis Streams vs RabbitMQ decision guide
- `context/stacks/nats-jetstream.md` — simpler alternative for fan-out without per-message routing
- `context/stacks/kafka.md` — better for log-style streams with schema registry and multi-consumer replay
- `context/stacks/coordination-seam-patterns.md` — broker seam pattern
- `context/stacks/duo-elixir-clojure.md` — primary RabbitMQ duo
- `examples/canonical-multi-backend/duos/elixir-clojure-rabbitmq/` — canonical seam example
