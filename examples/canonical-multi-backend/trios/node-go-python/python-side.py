# Seam example: Python ML service — FastAPI REST server (inbound from Go)
# Seam 2 of 2: Python ← Go via REST (Go calls POST /recommend for ML recommendation scores)
# Not a full application. See context/stacks/trio-node-go-python.md.
#
# In the primary topology (Node→Go→Python), Go calls this service after receiving a
# request from Node. Python returns recommendation scores; Go assembles the combined
# result and returns it to Node. Python is invisible to Node.
#
# Dependencies: fastapi, uvicorn
# Environment: PORT (default: 8002)

import os
import statistics
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="python-ml", docs_url=None, redoc_url=None)


class RecommendRequest(BaseModel):
    user_id: str
    features: list[float]


class Recommendation(BaseModel):
    score: float
    category: str
    reason: str


# ── Seam interaction: receive POST /recommend from Go ──
@app.post("/recommend", response_model=list[Recommendation])
def recommend(req: RecommendRequest) -> list[Recommendation]:
    """
    Stub recommendation logic:
    - score  = mean of feature values (or 0.5 if no features)
    - category = "premium" if score > 0.7 else "standard"
    - reason = "User profile score: {score:.2f}"

    In production this would call a trained model (e.g. scikit-learn, PyTorch).
    The list return demonstrates a realistic ML API that returns multiple candidates.
    """
    features = req.features
    score = statistics.mean(features) if features else 0.5
    score = round(score, 4)

    category = "premium" if score > 0.7 else "standard"
    reason = f"User profile score: {score:.2f}"

    print(
        f"[python-ml] recommend: user_id={req.user_id} "
        f"features={len(features)} score={score} category={category}"
    )

    return [Recommendation(score=score, category=category, reason=reason)]


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
