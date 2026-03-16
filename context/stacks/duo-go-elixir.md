# Duo: Go + Elixir

Go and Elixir combine to form a high-throughput, real-time event platform where Go owns the external-facing ingestion and API surface and Elixir owns the distributed state, fan-out, and live client delivery. Go excels at handling massive concurrent HTTP and gRPC connections efficiently; Elixir's BEAM runtime provides fault-tolerant process supervision, Phoenix Channels, and presence tracking that Go cannot match without reimplementing the OTP supervision model.

## Division of Labor

| Responsibility | Owner |
|---|---|
| External HTTP/gRPC API, auth, rate limiting | Go |
| Domain event ingestion and initial validation | Go |
| Distributed real-time state and presence | Elixir |
| WebSocket and Phoenix Channel fan-out to clients | Elixir |
| Fault-tolerant supervision and crash recovery | Elixir |
| Ops tooling, CLI workers, background I/O tasks | Go |
| Seam contract | Both |

## Primary Seam

Broker seam via NATS JetStream: Go publishes domain events to the `DOMAIN_EVENTS` stream, Elixir subscribes and fans them out to real-time WebSocket clients via Phoenix Channels.

## Communication Contract

Event schema on subject `events.domain.{entity_type}.{entity_id}`:

```json
{
  "payload_version": 1,
  "correlation_id": "req-abc-789",
  "published_at": "2026-03-16T10:30:00Z",
  "tenant_id": "acme",
  "entity_type": "order",
  "entity_id": "ord-555",
  "event_type": "order.confirmed",
  "data": {
    "total_cents": 4999,
    "line_items": 3
  }
}
```

Field notes:
- `payload_version`: consumers reject unknown versions
- `correlation_id`: propagated through downstream processing for tracing
- `event_type`: Elixir routes fan-out by this field; use reverse-DNS dot notation
- `data`: bounded — no embedded binary blobs; reference object storage for large payloads

## Local Dev Composition

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

  go-gateway:
    build:
      context: ./services/gateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      NATS_URL: nats://nats:4222
      PORT: "8080"
    depends_on:
      nats:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  elixir-coordinator:
    build:
      context: ./services/coordinator
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
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:4000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s
```

## Health Contract

- **go-gateway**: `GET /healthz` → `200 {"status":"ok"}`; degrades to `503` if NATS connection is lost
- **elixir-coordinator**: `GET /healthz` → `200 {"status":"ok"}` via Phoenix router; Gnat GenServer monitors connection state; supervisor restarts consumer on crash

## When to Use This Duo

- High-throughput data ingestion APIs (IoT telemetry, clickstream, payment events) feeding real-time dashboards and client notifications.
- Products where Go handles the ops-facing CLI tooling and batch workers while Elixir owns the live user-facing WebSocket layer.
- Multi-tenant SaaS where Go enforces per-tenant rate limiting at ingestion and Elixir maintains per-tenant presence and fan-out trees.
- Systems requiring independent scaling: Go instances scale horizontally for ingestion volume; Elixir nodes scale for client connection count.
- Teams that want Go's simplicity for the API layer but need BEAM's "let it crash" reliability for stateful real-time coordination.

## When NOT to Use This Duo

- Simple CRUD apps with no real-time requirements — a single Go service with Server-Sent Events is sufficient.
- The team has deep experience in one language only — the NATS seam is simple but two runtimes still doubles operational surface.
- Message volume is very high and a schema registry is needed — consider replacing NATS with Kafka and evaluating whether both languages are still justified.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/go-echo.md
- context/stacks/elixir-phoenix.md
- context/stacks/nats-jetstream.md
- context/stacks/coordination-seam-patterns.md
- examples/canonical-multi-backend/duos/go-elixir-nats/
