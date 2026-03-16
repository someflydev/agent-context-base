# Trio: Scala + Python + Go

The data platform trio: Scala owns distributed streaming and batch analytics (Akka Streams, Spark, or ZIO Streams), Python handles data science, complex aggregations, and model-based analysis on stream windows, and Go serves computed results through a lightweight operational API. The two design tensions this trio resolves are streaming scale vs. analytical depth (Scala's actor model and distributed execution handles volume and topology while Python's data science ecosystem handles depth of analysis on extracted windows) and analytical computation vs. fast serving (Python's batch-friendly computation is fully decoupled from Go's low-latency read API). The target archetype is a data-intensive platform: observability systems, analytics SaaS, streaming ML feature pipelines, BI tooling backends, or any system where a JVM streaming backbone feeds analytical workloads that are served to end clients.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Distributed streaming topology, stream windowing, Akka Streams / Spark coordination | Scala |
| Batch analytics pipeline definition, actor-model coordination across nodes | Scala |
| Data science analysis, complex aggregations, model training and inference on window data | Python |
| Ad-hoc analysis, pandas/polars transformations, Jupyter-style exploration pipelines | Python |
| Lightweight operational API, fast read endpoints for computed results | Go |
| Health monitoring, alerting hooks, ops integrations | Go |
| Seam A↔B contract (Scala → Python via REST or gRPC) | Scala + Python |
| Seam B↔C contract (Python → Go via REST) | Python + Go |

## Seam Map

Preferred topology (REST between all pairs):

```
[Scala Streaming]  ──── REST ────►  [Python Analytics]  ──── REST ────►  [Go API]
      :8080                               :8001                              :9090
```

Alternative topology (gRPC between Scala and Python when latency or schema enforcement matters):

```
[Scala Streaming]  ──── gRPC ────►  [Python Analytics]  ──── REST ────►  [Go API]
      :8080               :50051          :8001                              :9090
```

Scala extracts a stream window or batch result and calls Python with the data for analytical computation. Python writes the analysis result to a store that Go reads from, or POSTs the result directly to Go's ingest endpoint. Go serves those results to client dashboards, alerting systems, or external consumers.

Prefer REST for the Scala→Python seam unless latency profiling shows the REST overhead is measurable or unless the schema requires strict enforcement at the boundary. The gRPC seam adds proto compilation ceremony that is often not justified for analytical batch calls.

## Communication Contracts

### Seam A↔B: Scala → Python via REST

Request (`POST /analyze`):

```bash
curl -X POST http://python-service:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "window_id": "w-2026-03-16-1000",
    "window_start": "2026-03-16T10:00:00Z",
    "window_end": "2026-03-16T10:05:00Z",
    "metric": "request_latency_p99",
    "values": [12.1, 14.3, 11.8, 99.7, 13.2, 15.0]
  }'
```

Response:

```json
{
  "window_id": "w-2026-03-16-1000",
  "mean": 27.68,
  "p50": 13.75,
  "p99": 99.7,
  "anomaly_score": 0.73,
  "anomaly": true
}
```

### Alternative: Seam A↔B via gRPC

Proto file: `analytics.proto` (package `analytics.v1`)

```protobuf
syntax = "proto3";
package analytics.v1;

service AnalyticsService {
  rpc Analyze(AnalyzeRequest) returns (AnalyzeResponse);
}

message AnalyzeRequest {
  string          window_id    = 1;
  string          metric       = 2;
  repeated double values       = 3;
}

message AnalyzeResponse {
  string window_id     = 1;
  double mean          = 2;
  double p99           = 3;
  double anomaly_score = 4;
  bool   anomaly       = 5;
}
```

### Seam B↔C: Python → Go via REST

After analysis, Python POSTs results to Go:

Request (`POST /ingest/analysis-result`):

```bash
curl -X POST http://go-service:9090/ingest/analysis-result \
  -H "Content-Type: application/json" \
  -d '{
    "window_id": "w-2026-03-16-1000",
    "metric": "request_latency_p99",
    "anomaly": true,
    "anomaly_score": 0.73,
    "p99": 99.7,
    "computed_at": "2026-03-16T10:00:02Z"
  }'
```

Go clients read results:

```bash
curl http://go-service:9090/api/v1/windows/w-2026-03-16-1000/analysis
# {"window_id": "w-2026-03-16-1000", "anomaly": true, "anomaly_score": 0.73, ...}
```

## Local Dev Composition

```yaml
services:
  go-service:
    build: ./services/go
    ports:
      - "9090:9090"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9090/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  python-service:
    build: ./services/python
    ports:
      - "8001:8001"
    environment:
      PORT: "8001"
      GO_INGEST_URL: "http://go-service:9090"
    depends_on:
      go-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  scala-service:
    build: ./services/scala
    ports:
      - "8080:8080"
    environment:
      PYTHON_ANALYTICS_URL: "http://python-service:8001"
    depends_on:
      python-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 60s
```

## Health Contract

Dependency order (bottom to top):

1. **Go** — no application-level dependencies; starts first. Signals readiness at `GET /healthz → 200 {"status":"ok"}`. Python POSTs to Go, so Go must be ready before Python starts consuming and computing.
2. **Python** — depends on Go (direct). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after confirming Go's health endpoint is reachable. Python's ingest POST will fail if Go is not ready.
3. **Scala** — depends on Python (direct, which transitively implies Go is healthy). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after confirming Python's `/healthz`. Scala will not begin pushing stream windows to Python until Python is ready to receive and process them.

Note: Scala typically has a long JVM startup time (up to 60s with Spark or Akka). Set `start_period` accordingly and increase `retries` if needed.

## When to Use This Trio

- **Observability platforms**: Scala processes high-volume telemetry streams and extracts per-metric windows, Python runs anomaly detection or trend analysis on window data, Go serves alerting dashboards and ops integrations.
- **Analytics SaaS**: Scala handles customer event ingestion and session windowing at scale, Python computes cohort analytics and funnel analysis, Go serves the results to customer-facing dashboards via a low-latency API.
- **Streaming ML feature pipelines**: Scala extracts and aggregates real-time features from event streams, Python computes feature statistics and applies drift detection models, Go serves the feature store to downstream ML services.
- **BI tooling backends**: Scala coordinates batch and micro-batch analytics runs, Python handles complex statistical aggregations and reporting, Go provides fast query endpoints for BI client tools.

## When NOT to Use This Trio

- **Python can handle the streaming layer**: if volume is modest and the streaming topology is simple (a single consumer group processing events linearly), Python with Kafka/NATS consumers may suffice. Scala earns its place only when distributed execution, actor coordination, or Spark-scale batch analytics are genuinely required.
- **Go is not needed as a separate serving layer**: if the analytics results are consumed by the same Python service that computed them, or if Python can serve the API itself (e.g., FastAPI with acceptable latency), skip Go. Add Go only when the read API needs latency Go provides at lower operational complexity than Python.
- **Team does not operate JVM services**: Scala has a steep operational ramp (JVM tuning, Scala toolchain, sbt or Maven). If the team is not already JVM-comfortable, consider a Python-only pipeline with Go serving, or a Clojure alternative for the streaming layer.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/scala-tapir-http4s-zio.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/go-echo.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/duo-scala-rust.md`
- `context/stacks/duo-clojure-go.md`
