# Duo: Go + Python

Go and Python combine to form a production ML system where Go owns the entire request-handling layer — routing, authentication, rate limiting, and orchestration — and Python owns the scoring, recommendation, and analytics engine backed by its native ML ecosystem. Go handles connection volume at scale without GC pressure; Python provides unmatched access to PyTorch, scikit-learn, Polars, and the wider data science toolchain. This is the most operationally common polyglot duo because it maps cleanly onto how most ML teams are already organized.

## Division of Labor

| Responsibility | Owner |
|---|---|
| External API, routing, auth, rate limiting | Go |
| ML inference, scoring, and recommendation logic | Python |
| Request fan-out and response aggregation | Go |
| Feature pipeline, batch analytics, data transforms | Python |
| Service mesh glue and ops tooling | Go |
| Seam contract | Both |

## Primary Seam

REST seam via HTTP/JSON: Go sends `POST /score` requests to the Python scoring service, receives a typed JSON response, and returns the result to external callers — no proto ceremony required.

## Communication Contract

```
POST http://python-scoring:8001/score
Content-Type: application/json

{
  "features": [0.12, 0.98, 1.45, 0.33],
  "model": "fraud-v3"
}
```

Response:
```json
{
  "score": 0.87,
  "label": "high_risk",
  "latency_ms": 4.2
}
```

Error response (Python unavailable):
```json
HTTP 503
{"detail": "scoring service unavailable"}
```

FastAPI generates `/openapi.json` automatically — commit a snapshot to `docs/seam-contract/scoring-openapi.json`.

## Local Dev Composition

```yaml
services:
  python-scoring:
    build:
      context: ./services/scoring
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      PORT: "8001"
      MODEL_PATH: /models/fraud-v3.joblib
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  go-gateway:
    build:
      context: ./services/gateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      PYTHON_SCORE_URL: http://python-scoring:8001
      PORT: "8080"
    depends_on:
      python-scoring:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s
```

## Health Contract

- **python-scoring**: `GET /healthz` → `200 {"status":"ok"}` (FastAPI endpoint)
- **go-gateway**: `GET /healthz` → `200 {"status":"ok"}` normally; probes Python `/healthz` as a downstream check; returns `503 {"status":"degraded","reason":"scoring unavailable"}` if Python is unreachable

## When to Use This Duo

- Production ML serving where the Python team owns models and the platform team owns the API gateway — organizational seam maps to a language seam.
- Systems where the Go gateway enforces per-tenant rate limits, request signing, or JWT validation that Python should not need to implement.
- Analytics or recommendation engines where Python needs Polars, pandas, or scikit-learn and the API caller needs Go's concurrency for fan-out to multiple scoring endpoints.
- Gradual ML productionization: existing Go API service adds a Python scoring sidecar without rewriting the gateway.
- When REST is sufficient and the proto ceremony of gRPC is not justified — this is the default until call frequency or schema complexity demands gRPC.

## When NOT to Use This Duo

- Inference latency is critical (sub-5ms p99) and call frequency is very high — switch the seam to gRPC (see duo-rust-python.md for the extreme case).
- The ML logic is a simple lookup or rule set — implement it directly in Go and eliminate the Python service.
- Both services need to share the same Postgres schema for writes — this is one service wearing two hats; consolidate.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/go-echo.md
- context/stacks/python-fastapi-uv-ruff-orjson-polars.md
- context/stacks/coordination-seam-patterns.md
- examples/canonical-multi-backend/duos/go-python-rest/
