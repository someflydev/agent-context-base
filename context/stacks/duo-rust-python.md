# Duo: Rust + Python

Rust and Python combine to form a production AI platform where Python owns the full ML lifecycle — training, experimentation, and pipeline orchestration — and Rust serves trained models at inference time with predictable sub-millisecond latency. Neither language alone covers both halves well: Python's GIL and GC pauses are acceptable for batch training but unacceptable for high-frequency online inference; Rust can serve a model efficiently but cannot match Python's ML ecosystem for research and training.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Model training, experimentation, and batch pipelines | Python |
| Online inference serving (hot path) | Rust |
| Model artifact storage and versioning | Python |
| Inference RPC server (gRPC) | Rust |
| Training job orchestration and scheduling | Python |
| Seam contract | Both |

## Primary Seam

gRPC seam via Protocol Buffers: Python (or any caller) sends a `PredictRequest` to the Rust inference server, which loads the serialized model artifact and returns a typed `PredictResponse` with label, confidence, and duration.

## Communication Contract

```protobuf
// docs/seam-contract/inference.proto
syntax = "proto3";
package inference.v1;

service InferenceService {
  rpc Predict(PredictRequest) returns (PredictResponse);
}

message PredictRequest {
  string model_id  = 1;
  repeated float features = 2;
}

message PredictResponse {
  string label       = 1;
  float  confidence  = 2;
  int64  duration_ns = 3;
}
```

Python caller using `grpcio`:
```python
import grpc
import inference_pb2_grpc, inference_pb2

with grpc.insecure_channel("rust-inference:50051") as ch:
    stub = inference_pb2_grpc.InferenceServiceStub(ch)
    resp = stub.Predict(inference_pb2.PredictRequest(
        model_id="fraud-v3",
        features=[0.12, 0.98, 1.45],
    ))
    # resp.label, resp.confidence, resp.duration_ns
```

## Local Dev Composition

```yaml
services:
  rust-inference:
    build:
      context: ./services/inference
      dockerfile: Dockerfile
    image: rust:1.82-slim
    ports:
      - "50051:50051"
    environment:
      GRPC_PORT: "50051"
      MODEL_DIR: /models
    volumes:
      - model-artifacts:/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  python-ml:
    build:
      context: ./services/ml
      dockerfile: Dockerfile
    image: python:3.12-slim
    ports:
      - "8001:8001"
    environment:
      INFERENCE_ADDR: rust-inference:50051
      MODEL_DIR: /models
    volumes:
      - model-artifacts:/models
    depends_on:
      rust-inference:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

volumes:
  model-artifacts:
```

## Health Contract

- **rust-inference**: `GET /healthz` → `200 {"status":"ok"}` (HTTP sidecar alongside the gRPC port, or use `grpc.health.v1.Health/Check` via `grpc_health_probe`)
- **python-ml**: `GET /healthz` → `200 {"status":"ok"}` (FastAPI endpoint; degrades to `503` if the Rust inference address is unreachable)

## When to Use This Duo

- AI platform serving real-time predictions (fraud detection, recommendation, ad ranking) where training stays in Python and the serving SLA requires sub-10ms p99.
- Model inference is CPU/SIMD-bound and benefits from Rust's zero-overhead abstractions and ONNX/custom kernel integration.
- The Python ML team needs full ecosystem access (PyTorch, scikit-learn, Polars) without imposing those dependencies on the serving path.
- Canary model rollouts: Python pipeline publishes new model artifacts; Rust server hot-reloads them without restarting.
- Teams already operating Rust services who want to add ML without a Python-in-the-hot-path compromise.

## When NOT to Use This Duo

- Batch-only inference workloads with no latency SLA — Python alone (with multiprocessing or Ray) is sufficient and far simpler to operate.
- The model is a simple linear function or rule set — no language boundary needed; implement directly in the serving language.
- The team has no Rust experience — the gRPC boundary is manageable but the Rust inference server requires ownership; a Python-only serving stack (FastAPI + Gunicorn) may be adequate.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/rust-axum-modern.md
- context/stacks/python-fastapi-uv-ruff-orjson-polars.md
- context/stacks/coordination-seam-patterns.md
