# Seam: Node + Go + Python (REST + REST)

## Purpose

This example demonstrates both seams in the Node + Go + Python trio: Node resolves a GraphQL query by calling Go over REST (seam 1, Node → Go), and Go calls Python ML over REST to score recommendations (seam 2, Go → Python). Go acts as the internal orchestrator — it fetches domain data and calls Python ML, returning a single combined result to Node.

This is a **seam-focused example** — it shows only the coordination layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Architecture (Primary Topology)

```
[Node BFF]  ── REST ──►  [Go Services]  ── REST ──►  [Python ML]
  :3000                      :8080                       :8002
```

Node makes one call to Go. Go calls Python ML internally and returns a unified result. Python is invisible to Node.

## Why This Trio

**Node owns the BFF and GraphQL schema** — not Go. Node/TypeScript earns the BFF slot when client teams need GraphQL, schema evolution, or rapid frontend contract iteration. Go's API surfaces are stable and versioned; a GraphQL layer in front allows the schema to change without touching Go services.

**Go owns domain orchestration** — not Node. Go fetches user data, calls Python ML, and assembles the combined response. This keeps Node's resolver simple (one call to Go) and puts cross-service coordination logic in the language best suited for it: typed, reliable, easy to test.

**Python owns ML** — not Go. The recommendation scoring uses Python's ML ecosystem (scikit-learn, PyTorch). Python earns its place only when the team requires model serving, feature pipelines, or experiment tracking that cannot be replicated in Go.

## Two Topology Options

### Primary: Node → Go → Python (Go orchestrates)

```
[Node BFF]  ──►  [Go Services]  ──►  [Python ML]
```

Go calls Python internally. Node makes one call to Go and receives a combined `{user, recommendations}` result. This is the topology shown in this example.

**Choose when:**
- Go and Python serve a sequential pipeline (fetch data → score data)
- Node should not know whether ML features come from Python or a cache
- Go's domain layer adds business logic between the raw user data and the ML result
- You want a single downstream dependency for Node to manage

### Alternative: Node → Go (user data) + Node → Python (recommendations directly)

```
[Node BFF]  ──►  [Go Services]
    └──────────►  [Python ML]
```

Node calls Go for domain data and Python directly for ML scores. Node assembles the final response.

**Choose when:**
- Go and Python serve genuinely independent concerns that the BFF assembles
- The ML result is needed at the BFF layer for GraphQL field selection or subscription logic
- Python's response shape is not naturally a sub-field of a Go domain response
- Node has the context to decide how to merge the two responses (e.g., per-query logic)

**Trade-off:** The alternative gives Node more control but adds a Python dependency to Node's startup chain and requires the BFF to understand both Go's and Python's API contracts.

## Seam Types

**Seam 1 (Node → Go): REST (HTTP/JSON)**
**Seam 2 (Go → Python): REST (HTTP/JSON)**

Both seams use REST. This is the simplest trio topology — no broker, no gRPC ceremony — and the most common consumer product pattern.

## Seam 1: Node → Go via REST

### GraphQL query to REST translation

The GraphQL resolver calls `GET {GO_SERVICE_URL}/users/{userId}/recommendations`. Go returns a unified shape: `{user: {...}, recommendations: [...]}`. The resolver adds `userId` to each recommendation for the GraphQL type system.

```graphql
type Query {
  userWithRecommendations(userId: ID!): UserWithRecommendations
}
```

### Request

```bash
GET http://go-service:8080/users/u123/recommendations
```

### Response from Go (Node receives this)

```json
{
  "user": {"id": "u123", "name": "User u123", "email": "u123@example.com"},
  "recommendations": [{"score": 0.65, "category": "standard", "reason": "User profile score: 0.65"}]
}
```

### GraphQL response (Node sends this to the client)

```json
{
  "data": {
    "userWithRecommendations": {
      "user": {"id": "u123", "name": "User u123", "email": "u123@example.com"},
      "recommendations": [{"userId": "u123", "score": 0.65, "category": "standard", "reason": "User profile score: 0.65"}]
    }
  }
}
```

## Seam 2: Go → Python via REST

### Why REST (not gRPC)

For a recommendation scoring call with simple JSON payloads, REST is the right choice:
- The feature vector is small and JSON-serializable; proto binary encoding offers no meaningful gain
- FastAPI generates OpenAPI documentation automatically — the schema is self-describing
- The team can iterate on the Python API shape without regenerating stubs
- Use gRPC when performance matters at call frequency: repeated float arrays at high volume, sub-millisecond latency requirements, or when the Rust gRPC pattern (binary efficiency) is justified. For this consumer product stack, REST is sufficient.

### Request (Go → Python)

```bash
POST http://python-ml:8002/recommend
Content-Type: application/json

{"user_id": "u123", "features": [0.7, 0.1, 0.2, 0.3]}
```

### Response (Python → Go)

```json
[{"score": 0.325, "category": "standard", "reason": "User profile score: 0.33"}]
```

Python returns a **list** of recommendations — realistic ML APIs return multiple candidates; Go takes the list and passes it directly to Node.

## Dependency Ordering

```
python-ml   (no dependencies; starts first)
go-service  depends on: python-ml (service_healthy)
node-bff    depends on: go-service (service_healthy)
```

Strict linear chain. Go's `/healthz` probes Python (downstream health probe pattern). Node's `/healthz` probes Go. If Python is down, Go returns `503 {"status":"degraded","python_ml":"unavailable"}`, which propagates to Node's healthcheck.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/trios/node-go-python
docker compose up --build
```

Trigger a full round-trip:

```bash
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ userWithRecommendations(userId: \"u123\") { user { id name } recommendations { score category reason } } }"}'
```

Expected response:

```json
{
  "data": {
    "userWithRecommendations": {
      "user": {"id": "u123", "name": "User u123"},
      "recommendations": [{"score": 0.65, "category": "standard", "reason": "User profile score: 0.65"}]
    }
  }
}
```

## What to Observe

```
# Node logs (GraphQL resolver):
[node-bff] calling Go: GET http://go-service:8080/users/u123/recommendations
[node-bff] received from Go: user=u123 recommendations=1

# Go logs (domain service):
GET /users/u123/recommendations — received from Node BFF
Python ML result: userId=u123 recommendations=1

# Python logs (ML service, uvicorn access log):
[python-ml] recommend: user_id=u123 features=4 score=0.325 category=standard
INFO:     172.x.x.x:xxxxx - "POST /recommend HTTP/1.1" 200 OK
```

The downstream health probe chain:

```bash
curl http://localhost:8002/healthz   # Python → {"status":"ok"}
curl http://localhost:8080/healthz   # Go probes Python → {"status":"ok","python_ml":"ok"}
wget -O- http://localhost:3001/healthz  # Node probes Go → {"status":"ok"}
```

Stop Python and observe propagation:

```bash
docker compose stop python-ml
curl http://localhost:8080/healthz
# → 503 {"status":"degraded","python_ml":"unavailable"}
wget -O- http://localhost:3001/healthz
# → 503 {"status":"degraded","reason":"go-service unreachable"}
```

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/trio-node-go-python.md`
- `context/stacks/duo-node-go.md`
- `context/stacks/duo-go-python.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/typescript-hono-bun.md`
- `context/stacks/go-echo.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `examples/canonical-multi-backend/duos/node-go-rest/` — Node→Go REST duo (GraphQL BFF pattern)
- `examples/canonical-multi-backend/duos/go-python-rest/` — Go→Python REST duo (ML scoring)
