# Duo: Elixir + Clojure

Elixir and Clojure combine to form an event-driven platform where Clojure handles the intellectually dense work — complex data transformation, business rule engines, and Kafka Streams topology — and Elixir delivers the results reliably in real time to distributed clients. Both languages share an immutable-first, functional philosophy, which makes their event schemas translate cleanly across the seam. Clojure's LISP-family expressiveness and JVM ecosystem fit rich data processing; Elixir's BEAM runtime provides the fault-tolerant supervision and Phoenix Channels fan-out that Clojure cannot match.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Complex data transformation and enrichment | Clojure |
| Business rule engines and domain event processing | Clojure |
| Kafka/NATS Streams topology (if using Kafka) | Clojure |
| Real-time fan-out to connected clients | Elixir |
| Distributed state and multi-node presence | Elixir |
| Fault-tolerant supervision and crash recovery | Elixir |
| Client-facing WebSocket and Phoenix Channels | Elixir |
| Seam contract | Both |

## Primary Seam

Broker seam via NATS JetStream (or Kafka when schema registry and high throughput are required): Clojure produces enriched domain events; Elixir subscribes, fans them out to real-time clients via Phoenix Channels, and maintains distributed subscription state.

## Communication Contract

NATS subject: `events.domain.{entity_type}.{entity_id}`

Event schema:
```json
{
  "payload_version": 1,
  "correlation_id": "req-clj-777",
  "published_at": "2026-03-16T10:30:00Z",
  "entity_type": "position",
  "entity_id": "pos-443",
  "event_type": "position.updated",
  "data": {
    "lat": 37.7749,
    "lng": -122.4194,
    "speed_kmh": 42.1,
    "enrichment_version": "v2"
  }
}
```

Field notes:
- `enrichment_version`: tracks which Clojure enrichment pipeline version produced this event
- `event_type`: Elixir routes Phoenix Channel broadcasts by this field
- Both languages use immutable maps — data shapes translate without impedance

Kafka variant topic: `domain.positions.enriched` (use when throughput demands Kafka partitioning or schema registry is in place)

## Local Dev Composition

### NATS variant (default for local dev)

```yaml
services:
  nats:
    image: nats:2.10-alpine
    command: "-js -m 8222"
    ports:
      - "4222:4222"
      - "8222:8222"
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s

  clojure-processor:
    build:
      context: ./services/processor
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    environment:
      NATS_URL: nats://nats:4222
      INPUT_SUBJECT: events.raw.>
      OUTPUT_SUBJECT_PREFIX: events.domain
    depends_on:
      nats:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  elixir-fanout:
    build:
      context: ./services/fanout
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      NATS_URL: nats://nats:4222
      PHX_HOST: localhost
      PORT: "4000"
    depends_on:
      nats:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 25s
```

## Health Contract

- **clojure-processor**: `GET /healthz` → `200 {"status":"ok"}` (http-kit or Ring/Jetty handler); degrades if NATS connection is lost or consumer lag grows
- **elixir-fanout**: `GET /healthz` → `200 {"status":"ok"}` via Phoenix router; Gnat GenServer monitors connection and restarts on failure

## When to Use This Duo

- Real-time data platforms where Clojure data teams process and enrich events and Elixir delivers them to browser clients via Phoenix Channels.
- Financial trading or logistics platforms where business rules are complex enough to warrant Clojure's expressive data model and Elixir's BEAM reliability is needed for client delivery SLAs.
- Organizations with existing Clojure backend services that need to add a real-time client-facing layer without rewriting the processing tier.
- Products that are immutable-data-first across the stack — the functional philosophy of both languages minimizes translation friction at the seam.
- When NATS is sufficient for volume and simplicity; upgrade to Kafka if Clojure is already using Kafka Streams DSL and volume demands it.

## When NOT to Use This Duo

- The real-time delivery is simple (one server, a few clients) — Elixir alone handles both processing and delivery; no Clojure needed.
- The processing logic is straightforward map transforms — Go or Python can handle it without the JVM overhead.
- The team has experience in only one of these languages — this is one of the more unusual pairings; ensure both runtimes have operational owners before committing.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/elixir-phoenix.md
- context/stacks/nats-jetstream.md
- context/stacks/coordination-seam-patterns.md
