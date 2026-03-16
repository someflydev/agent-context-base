# Seam: Go + Python via REST (HTTP/JSON)

## Purpose

This example demonstrates the REST seam between a Go gateway service and a Python scoring service. Go receives external requests, calls Python's `/score` endpoint synchronously, and returns the scored result. The downstream health probe pattern is a key feature: Go's `/healthz` endpoint probes Python's `/healthz` and degrades gracefully if Python is unreachable.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**REST (synchronous, HTTP/JSON)** — Go calls Python; Python does not call Go.

## Why Go Is the Gateway and Python Owns Scoring

Go handles the request-handling concerns that scale under load: connection pooling, auth, rate limiting, and service mesh routing. It earns the gateway role because its concurrency model handles connection volume without GC pauses that would affect tail latency.

Python owns scoring because the ML model lives in the Python ecosystem (scikit-learn, PyTorch, ONNX). Moving inference to Go would mean losing the entire Python ML toolchain. The REST boundary is sufficient — the call frequency is low relative to the connection volume Go manages, and gRPC's proto ceremony is not justified at this stage.

The dependency is **unidirectional**: Go calls Python; Python does not call Go. If Python needs to trigger work in Go, a broker seam (NATS) or a webhook pattern is the right mechanism — not a reverse REST call.

## JSON Schema

Request (Go → Python, `POST /score`):
```json
{
  "features": [3.1, 7.2, 5.5, 2.9],
  "model": "fraud-v3"
}
```

Response (Python → Go):
```json
{
  "score": 0.72,
  "label": "high_risk",
  "latency_ms": 1.234
}
```

FastAPI generates an OpenAPI spec at `http://localhost:8001/openapi.json`. In production, commit a snapshot to `docs/seam-contract/scoring-openapi.json`.

## Downstream Health Probe Pattern

Go's `/healthz` endpoint **probes Python's `/healthz`** before returning a response:

- If Python is reachable and healthy: `200 {"status":"ok"}`
- If Python is unreachable or unhealthy: `503 {"status":"degraded","reason":"python scoring unreachable"}`

This ensures that `docker compose` healthchecks and upstream load balancers see an accurate picture of the full call path. A Go service that is running but cannot reach its downstream is not healthy.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/go-python-rest
docker compose up --build
```

Expected sequence:
1. `python-service` starts, passes its healthcheck.
2. `go-service` starts (after Python is healthy), connects, logs ready.
3. Trigger a round-trip: `curl http://localhost:8080/run-inference`

Expected response:
```json
{"score":0.72,"label":"high_risk","latency_ms":1.234}
```

## What to Observe

- Go log: `inference result: score=0.720 label=high_risk latency_ms=1.23`
- Python log: uvicorn access log showing `POST /score 200`
- Health endpoints:
  - `curl http://localhost:8001/healthz` → `{"status":"ok"}`
  - `curl http://localhost:8080/healthz` → `{"status":"ok"}` (Go probes Python)
- Stop Python, then check Go health: `docker compose stop python-service && curl http://localhost:8080/healthz` → `503`

## Upgrading to gRPC

If call frequency grows and the REST overhead is measurable, or if the schema becomes complex enough to benefit from proto enforcement, see:
- `context/stacks/coordination-seam-patterns.md` — gRPC seam pattern
- `examples/canonical-multi-backend/duos/kotlin-rust-grpc/` — gRPC canonical example

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-go-python.md`
- `context/stacks/go-echo.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/coordination-seam-patterns.md`
