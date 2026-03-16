# Seam: Node + Go via REST (HTTP/JSON) with GraphQL BFF

## Purpose

This example demonstrates the REST seam between a Node/TypeScript GraphQL BFF and a Go domain service. Node (Apollo Server) owns the client-facing GraphQL schema and resolves queries by calling Go's REST API. Go owns the domain data and its REST contract is simple, typed, and ignorant of GraphQL.

This example lightly previews the **GraphQL BFF pattern** before a dedicated `graphql.md` stack doc is added: Node is the natural home for the GraphQL schema layer; Go stays clean and REST-native.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**REST (synchronous, HTTP/JSON)** — Node calls Go; Go does not call Node. The dependency is unidirectional.

## Why REST (Not gRPC)

- **Simple request/response semantics are sufficient.** The Go domain API returns JSON objects; no binary encoding overhead is needed at this call frequency.
- **TypeScript `fetch` is idiomatic** — no proto compilation ceremony, no stub generation, no per-language toolchain.
- **Go's Echo REST API is already the natural surface.** Adding gRPC would require proto files, a build plugin, and stub generation in both Go and Node — real overhead for a pattern where JSON readability is valuable.

If call volume grows and binary encoding overhead becomes measurable, see `context/stacks/grpc.md` for the upgrade path.

## Why Node Handles GraphQL (Not Go)

- TypeScript's Apollo Server ecosystem (schema stitching, codegen, persisted queries, playground) is the right home for the GraphQL schema.
- Go stays clean and REST-native — its `/users` and `/users/:id` endpoints are reusable by any caller (REST clients, other BFFs, internal services) without GraphQL coupling.
- The BFF layer's job is client-specific shaping; Go's domain layer job is domain truth. Keeping them in separate services with a REST seam matches the organizational boundary.

## Topology

```
Client
  │  GraphQL POST /graphql
  ▼
node-bff (Apollo Server, port 3000)
  │  GET /users or /users/:id  (HTTP/REST)
  ▼
go-service (Echo, port 8080)
```

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/node-go-rest
docker compose up --build
```

Expected sequence:
1. `go-service` builds (fast — Go compile) and starts on `:8080`.
2. `node-bff` starts (after Go passes its healthcheck) on `:3000` (GraphQL) and `:3001` (/healthz).

## Sample GraphQL Queries

```bash
# Fetch all users
curl -X POST http://localhost:3000/graphql \
     -H "Content-Type: application/json" \
     -d '{"query":"{ users { id name email } }"}'
```

Expected response:
```json
{
  "data": {
    "users": [
      {"id":"1","name":"Alice Chen","email":"alice@example.com"},
      {"id":"2","name":"Bob Nakamura","email":"bob@example.com"},
      {"id":"3","name":"Carol Torres","email":"carol@example.com"}
    ]
  }
}
```

```bash
# Fetch a single user
curl -X POST http://localhost:3000/graphql \
     -H "Content-Type: application/json" \
     -d '{"query":"{ user(id: \"1\") { id name email createdAt } }"}'
```

```bash
# Fetch a non-existent user (returns null, not an error)
curl -X POST http://localhost:3000/graphql \
     -H "Content-Type: application/json" \
     -d '{"query":"{ user(id: \"99\") { id name } }"}'
```

## Port Layout

| Port | Service | Purpose |
|---|---|---|
| `8080` | go-service | REST domain API |
| `3000` | node-bff | GraphQL endpoint (Apollo Server) |
| `3001` | node-bff | HTTP /healthz (downstream health probe) |

The `/healthz` runs on a separate port (3001) because Apollo Server 4 standalone mode owns port 3000 entirely. The health server is a minimal Node `http.createServer` alongside the Apollo standalone server.

## Downstream Health Probe Pattern

Node's `/healthz` (on port 3001) probes the Go service's `/healthz` before responding. If Go is unreachable, Node returns `503`. This ensures `depends_on` chains and container orchestration see an accurate picture of the full call path.

```bash
# Verify health (probes go-service internally)
curl http://localhost:3001/healthz
# → {"status":"ok"}

# Stop Go, then check Node health:
docker compose stop go-service && curl http://localhost:3001/healthz
# → 503 {"status":"degraded","reason":"go-service unreachable"}
```

## Upgrading the Schema

The GraphQL schema in `node-side.ts` is intentionally minimal (one type, two queries). In production:
- Add mutations by defining them in `typeDefs` and calling Go `POST /users` from the resolver.
- Add field-level authorization by checking a token in the Apollo context object.
- Add `@apollo/server` persisted queries to reduce POST body size for frequent queries.
- See `context/stacks/duo-node-go.md` for the full Node + Go division of labor.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-node-go.md`
- `context/stacks/go-echo.md`
- `context/stacks/coordination-seam-patterns.md`
- `examples/canonical-multi-backend/duos/go-python-rest/` — REST seam without GraphQL layer
