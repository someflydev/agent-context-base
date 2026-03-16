# Duo: Node + Elixir

Node/TypeScript and Elixir combine to form a collaborative or multiplayer platform where Node owns the client connection layer — WebSocket/SSE sessions, custom protocol handling, client-specific auth, and BFF GraphQL subscriptions — and Elixir owns the authoritative distributed state: multi-node presence, channel lifecycle, crash recovery, and durable subscription state. Node connects clients to the seam; Elixir maintains the shared truth across the cluster. Neither language alone covers both concerns as well: Node's event loop handles client-side protocol diversity, but Elixir's BEAM handles multi-node distributed state with crash recovery that Node cannot replicate without significant operational complexity.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Client WebSocket and SSE connection management | Node/TypeScript |
| Client-specific auth token validation | Node/TypeScript |
| BFF GraphQL subscriptions and protocol adaptation | Node/TypeScript |
| Custom client protocol handling | Node/TypeScript |
| Authoritative distributed state across cluster nodes | Elixir |
| Multi-node presence and subscription tracking | Elixir |
| Channel lifecycle and fan-out coordination | Elixir |
| Crash recovery and durable subscription state | Elixir |
| Seam contract | Both |

## Primary Seam

Broker seam via NATS JetStream: Node publishes client actions to NATS; Elixir processes them, updates distributed state, and rebroadcasts state updates back through NATS to Node for delivery to connected clients.

## Communication Contract

Node → Elixir (client action), subject `actions.{session_id}.{action_type}`:
```json
{
  "payload_version": 1,
  "session_id": "sess-abc123",
  "correlation_id": "req-node-456",
  "published_at": "2026-03-16T10:30:00Z",
  "action_type": "cursor.moved",
  "data": {
    "x": 452,
    "y": 301,
    "doc_id": "doc-789"
  }
}
```

Elixir → Node (state broadcast), subject `state.{doc_id}.updates`:
```json
{
  "payload_version": 1,
  "doc_id": "doc-789",
  "published_at": "2026-03-16T10:30:00Z",
  "event_type": "presence.updated",
  "data": {
    "cursors": [
      {"session_id": "sess-abc123", "x": 452, "y": 301},
      {"session_id": "sess-def456", "x": 120, "y": 88}
    ]
  }
}
```

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

  node-gateway:
    build:
      context: ./services/gateway
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NATS_URL: nats://nats:4222
      PORT: "3000"
    depends_on:
      nats:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  elixir-state:
    build:
      context: ./services/state
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
      start_period: 25s
```

## Health Contract

- **node-gateway**: `GET /healthz` → `200 {"status":"ok"}`; degrades to `503` if NATS connection is lost; Node nats.js reconnects automatically but the health endpoint reflects connection state
- **elixir-state**: `GET /healthz` → `200 {"status":"ok"}` via Phoenix router; Gnat GenServer monitors NATS connection; OTP supervisor restarts consumers on crash

## When to Use This Duo

- Collaborative document editing or whiteboard apps where Node handles client WebSocket sessions and Elixir maintains the authoritative shared document state across cluster nodes.
- Multiplayer games where Node manages player connection and protocol adaptation and Elixir runs the authoritative game state with crash-safe process isolation.
- Live dashboards where Node serves the frontend-specific subscription API and Elixir fans out data updates across a multi-node cluster.
- Products where the client connection tier needs rapid iteration (protocol changes, client customization) without touching the distributed state layer.
- Teams with a Node/TypeScript frontend-adjacent team and a separate platform team who owns Elixir — the NATS seam maps cleanly to the organizational boundary.

## When NOT to Use This Duo

- Single-server collaborative apps with low concurrency — Elixir alone (Phoenix Channels) handles both client connections and state without Node.
- The client-facing layer is simple JSON REST — no WebSocket, no subscriptions, no protocol complexity — a Go or Elixir API service is sufficient.
- Real-time requirements are simple enough for Node alone — if a Node process with in-memory state is sufficient and multi-node distribution is not needed, don't add Elixir.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/elixir-phoenix.md
- context/stacks/nats-jetstream.md
- context/stacks/coordination-seam-patterns.md
