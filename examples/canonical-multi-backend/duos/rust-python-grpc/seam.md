# Seam: Rust + Python via gRPC (Protocol Buffers)

## Purpose

This example demonstrates the gRPC seam between a Rust inference server and a Python gRPC client. Rust owns the hot-path ML inference serving engine; Python acts as the orchestrator that calls it. This is the canonical AI platform pattern where the Python ML team retains full ecosystem access (grpcio, PyTorch, scikit-learn) while the serving path runs at Rust speed.

This is the inverse of `duos/kotlin-rust-grpc/` (where Kotlin is the caller and Rust is the server). Here Python is the caller and Rust is the server.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**gRPC (synchronous, Protocol Buffers)** — Python calls Rust; Rust serves.

## Why gRPC (Not REST)

- **Typed schema enforcement across language boundaries.** The `.proto` file is the canonical contract; both sides regenerate stubs from it. Breaking changes (field removal, renumbering) are caught at stub generation time rather than at runtime.
- **Binary encoding performance.** `repeated float features` fields serialize more compactly in proto binary than in JSON, which matters when feature vectors are large or call frequency is high.
- **Strong interface contract for the inference boundary.** ML teams often want to lock the inference API shape explicitly — proto enforces this more strictly than a JSON schema.

REST remains appropriate when call frequency is low and JSON readability outweighs the proto ceremony. See `context/stacks/coordination-seam-patterns.md` for the decision heuristic.

## Proto Contract

The seam contract lives in `service.proto`. Both sides regenerate from it:

- Package: `inference.v1` (distinct from `compute.v1` in kotlin-rust-grpc and `processing.v1` in go-rust-python trio)
- Service: `InferenceService.Predict(PredictRequest) returns (PredictResponse)`
- Request fields: `model_id`, `features` (repeated float), `correlation_id`
- Response fields: `label`, `confidence` (float), `duration_ns`

## Stub Generation Commands

### Rust (tonic-build — runs during `cargo build`)

```toml
# Cargo.toml [build-dependencies]
tonic-build = "0.12"
```

```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("service.proto")?;
    Ok(())
}
```

Requires `protoc` in the build environment: `apt-get install protobuf-compiler`.

### Python (grpcio-tools)

```bash
pip install grpcio-tools

python -m grpc_tools.protoc -I. \
    --python_out=. \
    --grpc_python_out=. \
    service.proto
```

Generates `inference_pb2.py` and `inference_pb2_grpc.py`. The Docker build runs this automatically.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/rust-python-grpc
docker compose up --build
```

Expected sequence:
1. `rust-server` builds from source (slow on first run — Rust compile) and starts; gRPC server listens on `:50051`; HTTP `/healthz` sidecar on `:8082`.
2. `python-caller` starts after Rust passes its healthcheck; generates proto stubs during image build.
3. Python fires a startup demo predict call and logs the result.

**Note:** the first `docker compose up --build` takes 5–10 minutes because Rust compiles all crates from source inside the container. Subsequent runs use the Docker layer cache and start in seconds.

## How to Verify

```bash
# POST to the Python service, which forwards to Rust via gRPC
curl -X POST http://localhost:8001/predict \
     -H "Content-Type: application/json" \
     -d '{"features":[0.8,0.6,0.9],"model_id":"demo"}'
```

Expected response:
```json
{"label":"positive","confidence":0.7666,"duration_ns":12345}
```

Try with low-confidence features:
```bash
curl -X POST http://localhost:8001/predict \
     -H "Content-Type: application/json" \
     -d '{"features":[0.1,0.2,0.3],"model_id":"demo"}'
```

Expected: `{"label":"low-confidence","confidence":0.2,"duration_ns":...}`

## What to Observe

- Python log: `[startup] demo predict OK: label=positive confidence=0.7200 duration_ns=<N>`
- Rust stderr: `predict model_id=demo correlation_id=startup-probe features=5 label=positive confidence=0.7200 duration_ns=<N>`
- Health endpoints:
  - `curl http://localhost:8082/healthz` → `{"status":"ok"}` (Rust HTTP sidecar)
  - `curl http://localhost:8001/healthz` → `{"status":"ok"}` (Python probes Rust — downstream health probe pattern)
- Stop Rust, then check Python health: `docker compose stop rust-server && curl http://localhost:8001/healthz` → `503`

## Downstream Health Probe Pattern

Python's `/healthz` does not just check if the Python process is alive — it fires a real gRPC `Predict` call to the Rust server. If Rust is unreachable or the call fails, Python returns `503`. This ensures that container orchestration (and `depends_on` chains) see an accurate picture of the full call path.

## Related

- `context/stacks/grpc.md` — full gRPC technical reference (stub generation, error codes, interceptors, streaming)
- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-rust-python.md`
- `context/stacks/rust-axum-modern.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/coordination-seam-patterns.md`
- `examples/canonical-multi-backend/duos/kotlin-rust-grpc/` — Kotlin caller + Rust server (compute.v1)
