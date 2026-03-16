# This is a seam-focused example.
# For a full application scaffold, see context/archetypes/multi-backend-service.md.
#
# python-side.py — Python scoring service: exposes POST /score and GET /healthz.
# Uses a deterministic stub model (no real ML) to keep the example self-contained.
# In production, replace stub_model() with a real model load and inference call.
#
# Dependencies (pyproject.toml or requirements.txt):
#   fastapi>=0.115
#   uvicorn[standard]>=0.30
#   pydantic>=2.0

import os
import time

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="scoring-service", version="0.1.0")


class ScoreRequest(BaseModel):
    features: list[float]
    model: str


class ScoreResponse(BaseModel):
    score: float
    label: str
    latency_ms: float


def stub_model(features: list[float], model: str) -> tuple[float, str]:
    """
    Deterministic stub — returns a score based on the mean of the input features.
    Replace with real model inference in production.
    """
    if not features:
        return 0.0, "no_input"
    mean = sum(features) / len(features)
    score = min(max(mean / 10.0, 0.0), 1.0)
    label = "high_risk" if score > 0.7 else "low_risk"
    return score, label


@app.post("/score", response_model=ScoreResponse)
async def score(request: ScoreRequest) -> ScoreResponse:
    start = time.monotonic()
    score_val, label = stub_model(request.features, request.model)
    latency_ms = (time.monotonic() - start) * 1000
    return ScoreResponse(score=score_val, label=label, latency_ms=round(latency_ms, 3))


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("python-side:app", host="0.0.0.0", port=port, reload=False)
