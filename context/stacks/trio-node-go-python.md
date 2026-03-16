# Trio: Node + Go + Python

The consumer product stack: Node/TypeScript owns the BFF (backend-for-frontend) layer and real-time client contracts, Go handles internal domain services and storage-backed APIs, and Python delivers ML-powered features like recommendations, ranking, and analytics. The two design tensions this trio resolves are frontend contract flexibility vs. domain service stability (the BFF absorbs schema churn from client teams without touching Go domain services) and domain correctness vs. intelligence (Go owns clean data models and business rules while Python augments them with ML-derived signals). The target archetype is a consumer product backend: e-commerce platforms with ML recommendations, social platforms with feed ranking, SaaS products with analytics dashboards, or any product where a JavaScript-native BFF tier is desirable.

## Division of Labor

| Responsibility | Owner |
|---|---|
| BFF layer, GraphQL schema, WebSocket/SSE sessions, client auth tokens | Node/TypeScript |
| Frontend-specific data shaping, field projection, client versioning | Node/TypeScript |
| Domain services, storage-backed CRUD, background workers, internal REST APIs | Go |
| Auth enforcement at domain boundary, service mesh routing | Go |
| ML recommendations, feed scoring, analytics, A/B experiment results | Python |
| Data science pipelines, model serving, batch analytics jobs | Python |
| Seam A↔B contract (Node → Go via REST) | Node + Go |
| Seam B↔C contract (Go → Python via REST) | Go + Python |

## Seam Map

Primary topology (Node calls Go, Go calls Python):

```
[Node BFF]  ──── REST ────►  [Go Services]  ──── REST ────►  [Python ML]
  :3000                           :8080                           :8001
```

Node receives a client request (e.g., "load home feed"), calls Go for domain data (user profile, followed entities, recent items), and optionally triggers a Python scoring call via Go. Go is the intermediary between the domain layer and the ML layer.

Alternative topology (Node calls both directly):

```
[Node BFF]  ──── REST ────►  [Go Services]
    :3000   └─── REST ────►  [Python ML]
                                 :8001
```

Node calls Go for domain data and Python directly for ML signals when the ML result is needed at the BFF layer without Go mediation (e.g., Go owns user profile data, Python owns recommendation scores, Node assembles the final feed response). Prefer this topology when Go and Python serve genuinely independent concerns that Node assembles, rather than a sequential pipeline.

## Communication Contracts

### Seam A↔B: Node → Go via REST (HTTP/JSON)

Request (`GET /api/v1/users/:id/feed`):

```bash
curl -H "Authorization: Bearer <token>" \
     http://go-service:8080/api/v1/users/u123/feed?limit=20
```

Response:

```json
{
  "user_id": "u123",
  "items": [
    {"item_id": "i001", "type": "post", "created_at": "2026-03-16T09:00:00Z"},
    {"item_id": "i002", "type": "article", "created_at": "2026-03-16T08:45:00Z"}
  ],
  "next_cursor": "cursor-abc"
}
```

Node's BFF layer reshapes this response for the client (e.g., merging with Python's ranking scores, projecting fields the client needs, applying client versioning).

### Seam B↔C: Go → Python via REST (HTTP/JSON)

Request (`POST /rank`):

```bash
curl -X POST http://python-service:8001/rank \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u123", "item_ids": ["i001", "i002", "i003"], "context": "home_feed"}'
```

Response:

```json
{
  "user_id": "u123",
  "ranked_items": [
    {"item_id": "i002", "score": 0.91, "reason": "high_affinity"},
    {"item_id": "i001", "score": 0.74, "reason": "recent_interaction"},
    {"item_id": "i003", "score": 0.52, "reason": "collaborative_filter"}
  ]
}
```

## Local Dev Composition

```yaml
services:
  python-service:
    build: ./services/python
    ports:
      - "8001:8001"
    environment:
      PORT: "8001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  go-service:
    build: ./services/go
    ports:
      - "8080:8080"
    environment:
      PYTHON_ML_URL: "http://python-service:8001"
      DATABASE_URL: "postgres://user:pass@postgres:5432/appdb"
    depends_on:
      python-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  node-service:
    build: ./services/node
    ports:
      - "3000:3000"
    environment:
      GO_SERVICE_URL: "http://go-service:8080"
      PYTHON_ML_URL: "http://python-service:8001"
    depends_on:
      go-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
```

## Health Contract

Dependency order (bottom to top):

1. **Python** — no dependencies; starts first. Signals readiness at `GET /healthz → 200 {"status":"ok"}`. Go cannot call Python until Python passes its healthcheck.
2. **Go** — depends on Python (direct). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after probing Python's health. Returns `503` if Python is unreachable.
3. **Node** — depends on Go (direct, which transitively implies Python is healthy). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after probing Go's health. In the direct topology (Node calls both Go and Python), Node also depends on Python directly.

If Node calls Python directly (alternative topology), add `python-service` to Node's `depends_on` as well.

## When to Use This Trio

- **E-commerce with ML recommendations**: Node/TypeScript owns the storefront BFF and GraphQL schema, Go manages catalog, orders, and inventory, Python runs the recommendation engine and A/B test result scoring.
- **Social platforms with feed ranking**: Node manages WebSocket sessions and SSE feeds, Go handles the post/user domain layer and storage, Python ranks feed items per user using collaborative filtering.
- **SaaS products with analytics dashboards**: Node provides the BFF with session and auth, Go handles billing, tenancy, and API logic, Python computes cohort analytics and usage predictions.
- **Consumer apps with AI features**: Node owns the mobile API surface and client-specific formatting, Go handles the stable domain layer, Python serves AI-powered features (smart search, natural language queries, churn prediction).
- All three are necessary because: Node earns the BFF slot when client teams need GraphQL, WebSocket, or rapid schema iteration that doesn't belong in Go services; Go earns the domain layer when reliability and storage-backed correctness matter; Python earns ML when the team uses PyTorch, scikit-learn, or similar ecosystems.

## When NOT to Use This Trio

- **Go can serve the BFF directly**: if the client API shape is stable and REST is sufficient, Go can serve clients without a Node BFF. Add Node only when GraphQL subscriptions, SSE, or client-versioned schema changes drive a genuine BFF need.
- **ML is simple enough for Go**: if the scoring logic is a lookup table or a simple linear model that can be expressed in Go, skip Python. Add Python only when the team requires the full Python ML ecosystem.
- **Small team, three languages is too much**: a three-language stack requires three deployment pipelines, three dependency ecosystems, and three sets of oncall runbooks. If the team is small, start with `duo-go-python` and add Node only when the BFF concern becomes real.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/typescript-hono-bun.md`
- `context/stacks/go-echo.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/duo-node-go.md`
- `context/stacks/duo-go-python.md`
- `context/stacks/duo-node-elixir.md`
