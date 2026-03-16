# Duo: Node + Go

Node/TypeScript and Go combine to form a consumer product backend where Node owns the frontend contract layer — BFF GraphQL schema, WebSocket sessions, OAuth flows, and client-specific data shaping — and Go owns the domain microservices: fast, storage-backed CRUD APIs, auth verification, and background workers. Node excels at rapid iteration on the client-facing API contract and rich JavaScript ecosystem integration; Go provides the concurrency and binary efficiency needed for the domain service tier that Node would struggle to match under load.

## Division of Labor

| Responsibility | Owner |
|---|---|
| GraphQL schema, BFF layer, client-specific shaping | Node/TypeScript |
| WebSocket and SSE client connections | Node/TypeScript |
| OAuth flows and client-facing token exchange | Node/TypeScript |
| Domain APIs: users, products, orders, auth verification | Go |
| Background workers and scheduled jobs | Go |
| Storage-backed CRUD and data persistence | Go |
| Seam contract | Both |

## Primary Seam

REST seam via HTTP/JSON: Node calls Go domain services over HTTP; Go services do not call Node (the dependency is unidirectional).

## Communication Contract

```
POST http://go-users:8080/users
Content-Type: application/json
Authorization: Bearer <internal-service-token>

{
  "email": "user@example.com",
  "display_name": "Alice"
}
```

Response:
```json
{
  "id": "usr-abc123",
  "email": "user@example.com",
  "display_name": "Alice",
  "created_at": "2026-03-16T10:30:00Z"
}
```

Node TypeScript client pattern:
```typescript
const GO_USERS_URL = process.env.GO_USERS_URL ?? "http://go-users:8080";

interface CreateUserReq { email: string; display_name: string }
interface User { id: string; email: string; display_name: string; created_at: string }

async function createUser(req: CreateUserReq): Promise<User> {
  const res = await fetch(`${GO_USERS_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`users service error: ${res.status}`);
  return res.json() as Promise<User>;
}
```

## Local Dev Composition

```yaml
services:
  go-users:
    build:
      context: ./services/users
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      PORT: "8080"
      DATABASE_URL: postgres://app:secret@postgres:5432/app
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  node-bff:
    build:
      context: ./services/bff
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      GO_USERS_URL: http://go-users:8080
      PORT: "3000"
    depends_on:
      go-users:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "app"]
      interval: 5s
      timeout: 3s
      retries: 5
```

## Health Contract

- **go-users** (and other Go domain services): `GET /healthz` → `200 {"status":"ok"}`; includes database connectivity check; degrades to `503` if Postgres is unreachable
- **node-bff**: `GET /healthz` → `200 {"status":"ok"}`; probes each downstream Go service; returns degraded status if any are unreachable

## When to Use This Duo

- Consumer products where the frontend team owns the BFF (GraphQL, REST aggregation) in TypeScript and the platform team owns Go domain APIs — organizational seam matches the language seam.
- Products with complex client-specific data shaping (e.g., mobile vs. web responses, localization, A/B variants) that belong in Node, keeping Go services clean and generic.
- Systems where Node handles WebSocket or SSE client connections that need to be maintained long-lived, while Go services handle the durable domain operations.
- When the Go service tier already exists and a TypeScript BFF is being added to aggregate and adapt it for a new client surface.
- Teams comfortable with TypeScript for rapid product iteration who do not want TypeScript's runtime in the critical domain service path.

## When NOT to Use This Duo

- Simple applications with one client type — a single Go service with JSON APIs is sufficient and removes the Node layer entirely.
- The BFF layer grows to own business logic — if Node starts doing domain work, consolidate into Go or reconsider boundaries.
- Real-time requirements are complex (multi-node presence, distributed state) — consider Node + Elixir (duo-node-elixir) instead, which handles distributed real-time coordination better than Node alone.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/go-echo.md
- context/stacks/coordination-seam-patterns.md
