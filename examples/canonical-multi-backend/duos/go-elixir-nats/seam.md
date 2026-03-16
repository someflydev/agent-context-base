# Seam: Go + Elixir via NATS JetStream (Broker)

## Purpose

This example demonstrates the broker seam between a Go service that ingests and publishes domain events and an Elixir service that subscribes and fans them out to real-time clients. The seam is NATS JetStream with durable consumers.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**Broker (async, decoupled)** — Go publishes; Elixir subscribes.

## Why Go Publishes and Elixir Subscribes

Go owns the ingestion layer: external HTTP/gRPC APIs, auth, rate limiting, and initial validation. It is the natural publisher because it handles the external boundary and determines when a domain event has occurred.

Elixir owns the distribution layer: it maintains durable subscriber state, supervises consumer processes, and fans events out to WebSocket clients via Phoenix Channels. The BEAM's "let it crash" supervisor model is better suited to long-lived subscription state than Go's goroutine model.

The seam is **unidirectional**: Go publishes, Elixir consumes. If Elixir needs to notify Go, a separate REST or gRPC call is the appropriate mechanism — not a second NATS topic in the reverse direction.

## Event Schema

Subject pattern: `events.{entity_type}.{tenant_id}`

```json
{
  "payload_version": 1,
  "correlation_id": "req-demo-001",
  "published_at": "2026-03-16T10:30:00Z",
  "tenant_id": "demo",
  "event_type": "user.created",
  "user_id": "u123"
}
```

- `payload_version`: Elixir consumers pattern-match on this; unknown versions are dropped with a warning log, not a crash.
- `event_type`: Elixir routes fan-out by this field using reverse-DNS dot notation.
- `correlation_id`: propagated through all downstream processing for distributed tracing.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/go-elixir-nats
docker compose up --build
```

Expected output:
1. NATS starts and passes its healthcheck.
2. `go-service` connects, ensures the `DOMAIN_EVENTS` stream, publishes one `user.created` event, and logs the publish ack.
3. `elixir-service` connects, ensures the same stream (idempotent), creates a durable consumer, and logs the received event: `event_type`, `user_id`, `correlation_id`.

## What to Observe

- Go log: `published user.created to "events.user.demo" (seq=1)`
- Elixir log: `received event type=user.created user_id=u123 topic=events.user.demo correlation_id=req-demo-001`
- NATS monitoring: `curl http://localhost:8222/jsz` shows stream `DOMAIN_EVENTS` with 1 message
- Health endpoints: `curl http://localhost:8080/healthz` and `curl http://localhost:4000/healthz` both return `{"status":"ok"}`

## Stream and Consumer Details

- Stream name: `DOMAIN_EVENTS`
- Stream subjects: `events.>`
- Consumer name: `elixir-consumer` (durable — survives restarts)
- Both services call `ensureStream` / `Gnat.Jetstream.API.Stream.create` on boot — safe to call multiple times

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-go-elixir.md`
- `context/stacks/go-echo.md`
- `context/stacks/elixir-phoenix.md`
- `context/stacks/nats-jetstream.md`
- `context/stacks/coordination-seam-patterns.md`
