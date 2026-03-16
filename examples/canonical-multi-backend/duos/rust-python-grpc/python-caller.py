# This is a seam-focused example.
# For a full application scaffold, see context/archetypes/multi-backend-service.md.
#
# python-caller.py — Python gRPC client calling the Rust InferenceService.
# Uses grpcio (C extension) for gRPC; FastAPI for the HTTP surface.
#
# Dependencies:
#   grpcio>=1.62
#   grpcio-tools>=1.62   (stub generation only — not imported at runtime)
#   fastapi>=0.115
#   uvicorn[standard]>=0.30
#   pydantic>=2.0
#
# Stub generation (run before starting this service):
#   python -m grpc_tools.protoc -I. \
#       --python_out=. --pyi_out=. --grpc_python_out=. \
#       service.proto
#
# Environment variables:
#   RUST_GRPC_URL  gRPC address of the Rust inference server (default: rust-server:50051)
#   HTTP_PORT      Port for this FastAPI service (default: 8001)

import os
import time

import grpc
import inference_pb2
import inference_pb2_grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

RUST_GRPC_URL: str = os.getenv("RUST_GRPC_URL", "rust-server:50051")
HTTP_PORT: int = int(os.getenv("HTTP_PORT", "8001"))

app = FastAPI(title="python-inference-caller", version="0.1.0")


# ---------------------------------------------------------------------------
# Request / Response shapes
# ---------------------------------------------------------------------------

class PredictIn(BaseModel):
    model_id: str
    features: list[float]


class PredictOut(BaseModel):
    label: str
    confidence: float
    duration_ns: int


# ---------------------------------------------------------------------------
# Startup demo call
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_demo() -> None:
    """
    On startup, send one demo PredictRequest to the Rust server to verify
    the gRPC seam is functional end-to-end.
    """
    demo_features = [0.8, 0.6, 0.9, 0.4, 0.7]
    try:
        with grpc.insecure_channel(RUST_GRPC_URL) as channel:
            stub = inference_pb2_grpc.InferenceServiceStub(channel)
            resp = stub.Predict(
                inference_pb2.PredictRequest(
                    model_id="demo",
                    features=demo_features,
                    correlation_id="startup-probe",
                ),
                timeout=10.0,
            )
        print(
            f"[startup] demo predict OK: label={resp.label} "
            f"confidence={resp.confidence:.4f} duration_ns={resp.duration_ns}"
        )
    except grpc.RpcError as e:
        print(f"[startup] demo predict FAILED: {e.code()} — {e.details()}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/healthz")
async def healthz() -> dict:
    """
    Downstream health probe pattern: this endpoint probes the Rust gRPC server.
    Returns 200 if reachable, 503 if the Rust server is unavailable.
    This ensures that container orchestration sees an accurate picture
    of the full call path — not just whether this Python process is alive.
    """
    try:
        with grpc.insecure_channel(RUST_GRPC_URL) as channel:
            stub = inference_pb2_grpc.InferenceServiceStub(channel)
            stub.Predict(
                inference_pb2.PredictRequest(
                    model_id="healthz",
                    features=[0.5],
                    correlation_id="healthz",
                ),
                timeout=2.0,
            )
        return {"status": "ok"}
    except grpc.RpcError:
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", "reason": "rust inference server unreachable"},
        )


@app.post("/predict", response_model=PredictOut)
async def predict(body: PredictIn) -> PredictOut:
    """
    Forward a predict request to the Rust gRPC server and return the result as JSON.
    Curl example:
      curl -X POST http://localhost:8001/predict \
           -H "Content-Type: application/json" \
           -d '{"features":[0.8,0.6,0.9],"model_id":"demo"}'
    """
    try:
        with grpc.insecure_channel(RUST_GRPC_URL) as channel:
            stub = inference_pb2_grpc.InferenceServiceStub(channel)
            resp = stub.Predict(
                inference_pb2.PredictRequest(
                    model_id=body.model_id,
                    features=body.features,
                    correlation_id="http-caller",
                ),
                timeout=5.0,
            )
        return PredictOut(
            label=resp.label,
            confidence=resp.confidence,
            duration_ns=resp.duration_ns,
        )
    except grpc.RpcError as e:
        status_code = 503 if e.code() == grpc.StatusCode.UNAVAILABLE else 500
        raise HTTPException(
            status_code=status_code,
            detail={"grpc_code": str(e.code()), "message": e.details()},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT)
