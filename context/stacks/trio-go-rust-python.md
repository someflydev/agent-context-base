# Trio: Go + Rust + Python

The performance pipeline trio: a Go gateway receives requests and orchestrates the full call sequence, a Rust kernel handles CPU-intensive preprocessing at low latency, and Python owns ML inference and advanced analytics. The two design tensions this trio resolves are throughput vs. compute density (Go routes requests efficiently while Rust saturates CPU cores without GC pauses) and compute preprocessing vs. intelligence (Rust normalizes or tokenizes data into a form Python's models can consume directly). The target archetype is a high-throughput data processing pipeline with ML scoring: AI search platforms, embedding pipelines, document processing at scale, and large-scale data enrichment with model inference.

## Division of Labor

| Responsibility | Owner |
|---|---|
| External API gateway, routing, auth, service mesh integration | Go |
| CPU-intensive preprocessing: tokenization, normalization, embedding computation, codec work | Rust |
| ML model inference, scoring, classification, advanced analytics | Python |
| gRPC client stub generation and Rust server call | Go + Rust |
| Feature vector handoff and REST scoring call | Go + Python |
| Seam A↔B contract (Go → Rust via gRPC) | Go + Rust |
| Seam B↔C contract (Go → Python via REST, using Rust output) | Go + Python |

## Seam Map

Primary topology (Go orchestrates both downstream services):

```
[Go Gateway]  ──── gRPC ────►  [Rust Kernel]
    :8080           :50051          │
      │                             │ preprocessed features
      │                             ▼
      └──────── REST ──────►  [Python ML]
                                   :8003
```

Go receives a request, calls Rust synchronously via gRPC to preprocess the input (tokenize, normalize, extract features), receives the feature vector from Rust, then calls Python via REST with those features to obtain the final score. Go assembles and returns the result. Rust and Python do not communicate directly.

This is a pipeline topology: Go is the orchestrator. Rust and Python are independent compute services that Go calls in sequence. Neither Rust nor Python needs to know about the other.

## Communication Contracts

### Seam A↔B: Go → Rust via gRPC

Proto file: `service.proto` (package `processing.v1`)

```protobuf
syntax = "proto3";
package processing.v1;

service ProcessService {
  rpc Preprocess(PreprocessRequest) returns (PreprocessResponse);
}

message PreprocessRequest {
  string document = 1;
  string doc_id   = 2;
}

message PreprocessResponse {
  repeated double features    = 1;
  int32           token_count = 2;
}
```

Both Go (client) and Rust (server) generate stubs from this file. Do not hand-write stubs.

Go calls Rust:
```bash
# Generated from service.proto
grpc_addr := os.Getenv("RUST_GRPC_URL")  # e.g. rust-service:50051
resp, err := client.Preprocess(ctx, &pb.PreprocessRequest{
    Document: "the quick brown fox",
    DocId:    "doc-001",
})
# resp.Features: [3.0, 5.0, 5.0, 3.0, 3.0]
# resp.TokenCount: 5
```

### Seam B↔C: Go → Python via REST (using Rust output)

Request (`POST /score`):

```bash
curl -X POST http://python-service:8003/score \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "doc-001", "features": [3.0, 5.0, 5.0, 3.0, 3.0], "token_count": 5}'
```

Response:

```json
{
  "doc_id": "doc-001",
  "score": 0.82,
  "category": "medium"
}
```

Go takes the `features` and `token_count` from Rust's gRPC response and passes them directly to Python's REST endpoint. Python never calls Rust.

## Local Dev Composition

```yaml
services:
  rust-service:
    build: ./services/rust
    ports:
      - "50051:50051"
      - "8090:8090"
    environment:
      GRPC_PORT: "50051"
      HTTP_PORT: "8090"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  python-service:
    build: ./services/python
    ports:
      - "8003:8003"
    environment:
      PORT: "8003"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  go-service:
    build: ./services/go
    ports:
      - "8080:8080"
    environment:
      RUST_GRPC_URL: "rust-service:50051"
      PYTHON_SCORE_URL: "http://python-service:8003"
    depends_on:
      rust-service:
        condition: service_healthy
      python-service:
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

1. **Rust** — no dependencies; starts first. Runs a gRPC server on `:50051` and an HTTP health sidecar on `:8090`. Signals readiness at `GET http://localhost:8090/healthz → 200 {"status":"ok"}`.
2. **Python** — no dependencies; starts first. Signals readiness at `GET /healthz → 200 {"status":"ok"}`.
3. **Go** — depends on both Rust and Python (direct). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after confirming it can reach both Rust gRPC (via a health probe or test call) and Python REST (`/healthz`). If either downstream is unreachable, Go returns `503 {"status":"degraded","reason":"..."}`.

Rust and Python have no `depends_on`. Go depends on both. This means Go will not accept traffic until both compute services are healthy.

## When to Use This Trio

- **AI search platforms**: Go handles query routing and auth, Rust tokenizes and normalizes query text into embedding-ready feature vectors, Python scores against a dense retrieval model.
- **Document processing pipelines at scale**: Go ingests document submissions, Rust performs CPU-bound text normalization and feature extraction, Python classifies or summarizes documents.
- **Embedding pipelines**: Go orchestrates batch or streaming document flows, Rust handles codec, normalization, and sliding-window tokenization, Python computes or applies embedding models.
- **Large-scale data enrichment with ML**: Go receives raw records from upstream producers, Rust normalizes and structurally validates them at high throughput, Python applies risk or quality scoring models.
- All three are necessary because: Go's throughput model handles the ingestion layer without blocking; Rust's zero-overhead compute is required for normalization work that would cause GC pauses in Go and doesn't belong in Python's interpreter; Python's ML ecosystem is irreplaceable for the model inference step.

## When NOT to Use This Trio

- **Light preprocessing**: if the normalization work is simple (lowercase, split on whitespace), Go can do it inline and Python can receive raw text. Add Rust only when CPU profiling shows preprocessing is a measurable bottleneck.
- **Python handles both preprocessing and inference**: if the ML team owns the full pipeline and the preprocessing is Python-idiomatic (spaCy, HuggingFace tokenizers), don't introduce Rust just for tokenization — the seam cost outweighs the benefit.
- **No ML involved**: if the downstream processing is not model-based, consider `duo-go-rust` with a gRPC seam; Python is not needed.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/go-echo.md`
- `context/stacks/rust-axum-modern.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/duo-go-python.md`
- `context/stacks/duo-kotlin-rust.md`
- `examples/canonical-multi-backend/trios/go-rust-python/`
