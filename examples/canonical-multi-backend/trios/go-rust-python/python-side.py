# Seam example: Python ML service — REST scoring endpoint
# This file shows only the seam layer: /score endpoint and /healthz.
# Scoring is a deterministic stub — not real ML.
# Input features come from Rust's Preprocess gRPC response (via Go).
# See context/stacks/trio-go-rust-python.md for architecture context.

import os
import statistics
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="python-ml-service")


class ScoreRequest(BaseModel):
    doc_id: str
    features: list[float]
    token_count: int


class ScoreResponse(BaseModel):
    doc_id: str
    score: float
    category: str


def stub_score(features: list[float], token_count: int) -> tuple[float, str]:
    """
    Deterministic stub scoring function.
    score  = mean of features (word lengths), normalized to [0, 1] over range 0–15
    category derived from token_count:
      short  (<= 5 tokens)
      medium (6–20 tokens)
      long   (> 20 tokens)
    In production, replace with: model.predict(features, token_count).
    """
    if not features:
        score = 0.0
    else:
        score = round(min(max(statistics.mean(features) / 15.0, 0.0), 1.0), 4)

    if token_count <= 5:
        category = "short"
    elif token_count <= 20:
        category = "medium"
    else:
        category = "long"

    return score, category


# Seam B↔C inbound: Go calls POST /score with Rust-preprocessed features
@app.post("/score", response_model=ScoreResponse)
async def score(request: ScoreRequest) -> ScoreResponse:
    score_val, category = stub_score(request.features, request.token_count)
    return ScoreResponse(
        doc_id=request.doc_id,
        score=score_val,
        category=category,
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
