# Seam example: Python inference service — REST scoring endpoint
# This file shows only the seam layer: /score endpoint and /healthz.
# Scoring is a deterministic stub — not real ML.
# See context/stacks/trio-go-elixir-python.md for architecture context.

import os
import statistics
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="python-inference-service")


class ScoreRequest(BaseModel):
    job_id: str
    features: list[float]


class ScoreResponse(BaseModel):
    job_id: str
    score: float
    label: str


def stub_score(features: list[float]) -> tuple[float, str]:
    """
    Deterministic stub scoring function.
    In production, replace with: model.predict(features).
    """
    if not features:
        return 0.0, "unknown"
    mean = statistics.mean(features)
    # Normalize to [0, 1] assuming feature range 0–10
    score = min(max(mean / 10.0, 0.0), 1.0)
    label = "high_value" if score >= 0.7 else ("medium_value" if score >= 0.4 else "low_value")
    return round(score, 4), label


# Seam B↔C inbound: Elixir calls POST /score
@app.post("/score", response_model=ScoreResponse)
async def score(request: ScoreRequest) -> ScoreResponse:
    score, label = stub_score(request.features)
    return ScoreResponse(
        job_id=request.job_id,
        score=score,
        label=label,
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
