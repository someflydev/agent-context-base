# Seam: Go + Rust + Python (gRPC + REST)

## Purpose

This example demonstrates both seams in the Go + Rust + Python trio: Go calls Rust synchronously via gRPC to preprocess a document (seam A↔B), then calls Python synchronously via REST with the preprocessed features to score it (seam B↔C). Go is the orchestrator — it owns the pipeline and assembles the final result. Rust and Python do not communicate with each other.

This is a **seam-focused example** — it shows only the coordination layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Types

**Seam A↔B: gRPC (synchronous, typed)** — Go calls Rust `ProcessService.Preprocess`.
**Seam B↔C: REST (synchronous)** — Go calls Python `POST /score` with Rust's output.

## Why Go Orchestrates Both Seams

Go receives the request, knows it needs two downstream steps (preprocess, then score), and orchestrates both. This is the pipeline topology: Go calls Rust, takes the result, and passes it to Python. Neither Rust nor Python need to know about each other. Rust is a stateless compute service; Python is a stateless scoring service. Go assembles the pipeline.

An alternative where Rust calls Python directly would require Rust to maintain an HTTP client, understand Python's API schema, and handle Python failure modes — all concerns that belong to Go as the orchestrator.

## Proto File

`service.proto` uses package `processing.v1`, distinct from the `compute.v1` package in `duos/kotlin-rust-grpc/`. Each seam example has its own package namespace.

```protobuf
service ProcessService {
  rpc Preprocess(PreprocessRequest) returns (PreprocessResponse);
}
message PreprocessRequest  { string document = 1; string doc_id = 2; }
message PreprocessResponse { repeated double features = 1; int32 token_count = 2; }
```

## Stub Generation Commands

### Rust (tonic + prost via build.rs)

```bash
# build.rs handles this automatically:
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("service.proto")?;
    Ok(())
}

# Manual (if needed):
cargo install protoc-gen-prost protoc-gen-tonic
protoc --prost_out=src/gen --tonic_out=src/gen service.proto
```

### Go (protoc-gen-go + protoc-gen-go-grpc)

```bash
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest

protoc --go_out=. --go-grpc_out=. \
       --go_opt=paths=source_relative \
       --go-grpc_opt=paths=source_relative \
       service.proto
# Generates: gen/processing/v1/service.pb.go and service_grpc.pb.go
```

## JSON Schemas

### Go → Rust (gRPC PreprocessRequest)

```json
{"document": "the quick brown fox jumps over", "doc_id": "doc-001"}
```

### Rust → Go (gRPC PreprocessResponse)

```json
{"features": [3.0, 5.0, 5.0, 3.0, 5.0, 4.0], "token_count": 6}
```

### Go → Python (REST POST /score)

```json
{"doc_id": "doc-001", "features": [3.0, 5.0, 5.0, 3.0, 5.0, 4.0], "token_count": 6}
```

### Python → Go (REST response)

```json
{"doc_id": "doc-001", "score": 0.2667, "category": "medium"}
```

## How to Run Locally

```bash
cd examples/canonical-multi-backend/trios/go-rust-python
docker compose up --build
```

Note: the first build takes several minutes — Rust compiles from source.

Expected sequence:
1. `rust-service` builds, starts gRPC on `:50051`, starts HTTP health sidecar on `:8090`.
2. `python-service` starts and passes its healthcheck on `:8003`.
3. `go-service` starts after both Rust and Python are healthy.

Trigger a full pipeline round-trip:

```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{"document": "the quick brown fox jumps over the lazy dog", "doc_id": "doc-001"}'
```

Expected response:

```json
{"doc_id": "doc-001", "score": 0.2933, "category": "medium"}
```

## What to Observe

- Go log: `rust preprocess doc_id=doc-001 token_count=9 features=[3 5 5 3 5 4 3 4 3]`
- Go log: `python score doc_id=doc-001 score=0.293300 category=medium`
- Rust stderr: `preprocess doc_id=doc-001 token_count=9 features=[3, 5, 5, 3, 5, 4, 3, 4, 3]`
- Python log: uvicorn access log `POST /score 200`
- Health endpoints:
  - `curl http://localhost:8090/healthz` → `{"status":"ok"}` (Rust HTTP sidecar)
  - `curl http://localhost:8003/healthz` → `{"status":"ok"}` (Python)
  - `curl http://localhost:8080/healthz` → `{"status":"ok"}` (Go — probes both Rust and Python)

Stop Python and check Go health:
```bash
docker compose stop python-service
curl http://localhost:8080/healthz
# → 503 {"status":"degraded","rust_ok":true,"python_ok":false}
```

## Dependency Order

Rust and Python start first with no dependencies. Go starts after both pass their healthchecks. Go's `/healthz` actively probes both Rust (gRPC) and Python (REST) — a failing downstream makes Go degrade to `503`.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/trio-go-rust-python.md`
- `context/stacks/duo-kotlin-rust.md`
- `context/stacks/duo-go-python.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/go-echo.md`
- `context/stacks/rust-axum-modern.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
