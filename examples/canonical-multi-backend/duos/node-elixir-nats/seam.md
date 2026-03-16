# Seam: Node + Elixir via NATS (Broker, Bidirectional)

## Purpose

This example demonstrates the bidirectional NATS broker seam between a Node/TypeScript service (client connection layer) and an Elixir service (distributed state). Node publishes client actions to NATS; Elixir processes them, updates distributed state, and publishes state updates back through NATS to Node for delivery to connected clients.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**Broker (bidirectional, core NATS)** — Node publishes client actions; Elixir subscribes and processes; Elixir publishes state updates; Node subscribes and receives.

## Division of Subjects

| Direction | Subject pattern | Owner | Description |
|---|---|---|---|
| Node → Elixir | `actions.{session_id}.{action_type}` | Node publishes | Client action (cursor move, key press, etc.) |
| Elixir → Node | `state.{doc_id}.updates` | Elixir publishes | State broadcast (presence, document state) |

Node subscribes to `state.*.updates` to receive all state broadcasts. Elixir subscribes to `actions.>` to receive all client actions.

## Why Bidirectional (not unidirectional)

The `go-elixir-nats` example is **unidirectional**: Go publishes, Elixir subscribes. That pattern is appropriate when one service owns the ingestion boundary and the other owns distribution.

This example is **bidirectional** because the collaborative app use case requires both directions:

- **Client actions go Node → Elixir.** Node owns the client connection layer — it receives WebSocket messages from clients and must forward them to Elixir for state processing. Node cannot update Elixir's authoritative state directly.
- **State updates go Elixir → Node.** Elixir processes the action, updates distributed state, and must push the new state to Node so Node can relay it to connected clients. This push must be **asynchronous** — a client may be connected and idle when a state update arrives from another client's action.

REST would require Node to poll Elixir for state updates — wasteful and high-latency for real-time coordination. NATS subjects let Elixir push to Node the moment state changes.

## Why Core NATS (not JetStream)

This example uses **core NATS** (no JetStream). JetStream adds durable persistence, at-least-once delivery, and durable consumers. For this use case, those features are unnecessary:

- **Ephemeral real-time coordination.** Cursor positions and presence state are ephemeral — a message that was not delivered because a client was briefly disconnected does not need to be replayed. The next state update will supersede it.
- **Simplicity.** Core NATS requires no stream or consumer creation on startup. Both sides just connect and subscribe/publish.
- **Contrast with `go-elixir-nats`.** That example uses JetStream because it processes domain events (e.g., `user.created`) that must not be lost — durable persistence and at-least-once delivery are required. For cursor movements, durable delivery would be an over-engineering of the seam.

If your use case requires durability (e.g., collaborative document operations that must be replayed on reconnect), switch to JetStream and follow the `nats-jetstream.md` patterns.

## The Two Subject Namespaces

### `actions.{session_id}.{action_type}` — Node → Elixir

Published by Node when a client sends an action. Examples:
- `actions.sess-abc123.cursor.moved`
- `actions.sess-xyz456.key.pressed`
- `actions.sess-abc123.selection.changed`

Elixir subscribes to `actions.>` — the `>` wildcard matches all remaining tokens, so Elixir receives all actions regardless of session or type.

### `state.{doc_id}.updates` — Elixir → Node

Published by Elixir after processing an action and updating state. Examples:
- `state.doc-789.updates`
- `state.doc-abc.updates`

Node subscribes to `state.*.updates` — the `*` wildcard matches one token (the doc_id), so Node receives state updates for all documents.

## Message Payloads

### Node → Elixir (client action)

```json
{
  "payload_version": 1,
  "session_id": "sess-demo",
  "correlation_id": "demo-001",
  "published_at": "2026-03-16T10:30:00Z",
  "action_type": "cursor.moved",
  "data": {
    "x": 100,
    "y": 200,
    "doc_id": "doc-abc"
  }
}
```

### Elixir → Node (state update)

```json
{
  "payload_version": 1,
  "doc_id": "doc-abc",
  "published_at": "2026-03-16T10:30:01Z",
  "event_type": "presence.updated",
  "data": {
    "cursors": [
      {"session_id": "sess-demo", "x": 100, "y": 200}
    ]
  }
}
```

Both payloads include `payload_version`. Consumers must check this field and drop or log messages with unknown versions rather than processing them with the wrong field map.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/node-elixir-nats
docker compose up --build
```

Expected sequence:
1. NATS starts and passes its healthcheck.
2. `node-service` and `elixir-service` start after NATS is healthy.
3. Node publishes one demo action to `actions.sess-demo.cursor.moved`.
4. Elixir receives the action, logs it, and publishes a state update to `state.doc-abc.updates`.
5. Node receives the state update and logs it.

## What to Observe

- **Node logs:**
  ```
  NATS connected
  Subscribed to state.*.updates
  published action to "actions.sess-demo.cursor.moved" correlation_id=demo-001
  state update received event_type=presence.updated doc_id=doc-abc data={"cursors":[...]}
  ```
- **Elixir logs:**
  ```
  NATS connected to nats://nats:4222
  Subscribed to actions.>
  received action type=cursor.moved session_id=sess-demo doc_id=doc-abc topic=actions.sess-demo.cursor.moved
  published state update to state.doc-abc.updates event_type=presence.updated
  ```
- **NATS monitoring:** `curl http://localhost:8222/varz` shows connection counts.
- **Health endpoints:**
  - `curl http://localhost:3000/healthz` → `{"status":"ok"}` (Node/Hono)
  - `curl http://localhost:4000/healthz` → `{"status":"ok"}` (Elixir/Phoenix)

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-node-elixir.md`
- `context/stacks/nats-jetstream.md`
- `context/stacks/elixir-phoenix.md`
- `context/stacks/coordination-seam-patterns.md`
- `examples/canonical-multi-backend/duos/go-elixir-nats/` — unidirectional NATS seam (Go → Elixir) with JetStream
