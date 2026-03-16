# Trio: Go + Elixir + Python

The canonical AI platform trio: a Go gateway absorbs high-throughput external traffic, an Elixir coordinator manages distributed job queuing and fault-tolerant retries, and Python owns ML model inference. The two design tensions this trio resolves are throughput vs. coordination (Go and Elixir each serve their concern without compromise) and coordination vs. intelligence (Elixir's OTP supervision model keeps inflight jobs reliable, while Python's ecosystem handles the actual scoring). The target archetype is a real-time AI platform: recommendation engines, fraud detection pipelines, content moderation systems, or any flow where external requests must be enriched by ML inference at scale.

## Division of Labor

| Responsibility | Owner |
|---|---|
| External HTTP ingestion, auth, rate limiting, high-throughput routing | Go |
| Distributed job coordination, in-flight tracking, fault-tolerant retries | Elixir |
| Result fan-out to real-time clients via Phoenix Channels / WebSocket | Elixir |
| ML model inference, feature extraction, scoring, batch analytics | Python |
| Stream setup and NATS JetStream publishing of inference jobs | Go |
| Job distribution and NATS consumer supervision | Elixir |
| Seam A↔B contract (Go → Elixir via NATS JetStream) | Go + Elixir |
| Seam B↔C contract (Elixir → Python via REST HTTP/JSON) | Elixir + Python |

## Seam Map

```
[Go Gateway]  ──── NATS JetStream ────►  [Elixir Coordinator]
  :8080                                        :4000
                                                 │
                                            REST (HTTP)
                                           POST /score
                                                 ▼
                                         [Python Inference]
                                               :8002
```

Go publishes inference jobs to the `jobs.submitted` NATS subject. Elixir subscribes, distributes jobs to worker processes, calls Python's `/score` endpoint synchronously for each job, and publishes the scored result back to `jobs.scored` for real-time delivery to connected clients.

Elixir is the coordinator, not a pass-through. It manages the job queue, tracks in-flight inferences, handles retries when Python is slow or unavailable, and owns the fan-out to any number of downstream consumers or WebSocket connections.

## Communication Contracts

### Seam A↔B: Go → Elixir via NATS JetStream

Stream: `JOBS`, subjects: `jobs.>`

Event published to `jobs.submitted`:

```json
{
  "payload_version": 1,
  "correlation_id": "req-abc-001",
  "published_at": "2026-03-16T10:00:00Z",
  "job_id": "job-xyz-42",
  "features": [1.2, 3.4, 5.6, 7.8],
  "model": "scoring-v2"
}
```

- `payload_version`: Elixir pattern-matches on this; unknown versions are logged and dropped, not crashed.
- `correlation_id`: propagated through all downstream calls for distributed tracing.
- `job_id`: stable identifier used by Elixir to deduplicate and track in-flight state.

Elixir publishes results to `jobs.scored`:

```json
{
  "payload_version": 1,
  "correlation_id": "req-abc-001",
  "job_id": "job-xyz-42",
  "score": 0.87,
  "label": "high_value",
  "scored_at": "2026-03-16T10:00:01Z"
}
```

### Seam B↔C: Elixir → Python via REST (HTTP/JSON)

Request (`POST /score`):

```bash
curl -X POST http://python-service:8002/score \
  -H "Content-Type: application/json" \
  -d '{"job_id": "job-xyz-42", "features": [1.2, 3.4, 5.6, 7.8]}'
```

Response:

```json
{
  "job_id": "job-xyz-42",
  "score": 0.87,
  "label": "high_value"
}
```

FastAPI auto-generates an OpenAPI spec at `/openapi.json`. In production, commit a snapshot to `docs/seam-contract/scoring-openapi.json`.

## Local Dev Composition

```yaml
services:
  nats:
    image: nats:2.10-alpine
    command: "-js"
    ports:
      - "4222:4222"
      - "8222:8222"
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s

  python-service:
    build: ./services/python
    ports:
      - "8002:8002"
    environment:
      PORT: "8002"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  elixir-service:
    build: ./services/elixir
    ports:
      - "4000:4000"
    environment:
      NATS_URL: "nats://nats:4222"
      PYTHON_SCORE_URL: "http://python-service:8002"
    depends_on:
      nats:
        condition: service_healthy
      python-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  go-service:
    build: ./services/go
    ports:
      - "8080:8080"
    environment:
      NATS_URL: "nats://nats:4222"
    depends_on:
      nats:
        condition: service_healthy
      elixir-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
```

## Health Contract

Dependency order (bottom to top):

1. **Python** — no dependencies; starts first. Signals readiness at `GET /healthz → 200 {"status":"ok"}`. Elixir cannot call Python until Python passes its healthcheck.
2. **NATS** — no dependencies; starts first. Signals readiness at `http://nats:8222/healthz`. Both Go and Elixir depend on NATS.
3. **Elixir** — depends on NATS (direct) and Python (direct). Signals readiness at `GET /healthz → 200 {"status":"ok"}` only after its NATS subscription is established and its HTTP client can reach Python.
4. **Go** — depends on NATS (direct) and Elixir (transitive: Elixir health implies Python and NATS are also healthy). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after confirming NATS JetStream is reachable.

Python and NATS have no `depends_on`. Elixir depends on both. Go depends on NATS and Elixir. This cascading structure ensures no service starts publishing before its downstream is ready to receive.

## When to Use This Trio

- **Real-time recommendation engines**: Go handles the burst of product-page requests, Elixir distributes scoring jobs and delivers results to WebSocket clients, Python runs the recommendation model.
- **Fraud detection pipelines**: Go ingests transactions at high throughput, Elixir coordinates in-flight detection jobs with per-transaction state and retries, Python scores feature vectors against a fraud model.
- **Content moderation platforms**: Go receives content submission events from external webhooks, Elixir fans moderation jobs across worker processes, Python runs classifier models.
- **IoT telemetry + ML scoring**: Go ingests device events at scale, Elixir coordinates per-device job queues and handles device disconnects gracefully, Python scores sensor readings against anomaly detection models.
- All three languages are necessary because: Go's throughput model cannot be replaced by Elixir for the ingestion layer; Elixir's OTP supervision cannot be replaced by Go for stateful job coordination at scale; Python's ML ecosystem cannot be replaced by either for inference.

## When NOT to Use This Trio

- **A duo suffices**: if ML inference is occasional and Python is called directly from Go without coordination overhead, use the `duo-go-python` stack. Add Elixir only when you need distributed job state, fan-out, or supervisor-managed retries.
- **Low volume inference**: if the scoring load is low and reliability can be handled with simple Go retry logic, the Elixir coordination layer adds ops overhead without payoff.
- **No real-time delivery required**: if scored results are returned synchronously in the HTTP response (simple request-response), the async NATS-based architecture is over-engineered. Use `duo-go-python` with a REST seam.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/go-echo.md`
- `context/stacks/elixir-phoenix.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/duo-go-elixir.md`
- `context/stacks/duo-go-python.md`
- `examples/canonical-multi-backend/trios/go-elixir-python/`
