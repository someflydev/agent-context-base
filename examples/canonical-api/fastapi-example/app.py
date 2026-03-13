from __future__ import annotations

from fastapi import FastAPI


app = FastAPI()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "fastapi-example"}


@app.get("/reports/summary")
async def report_summary(tenant_id: str, limit: int = 10) -> list[dict[str, object]]:
    rows = [
        {"report_id": "daily-signups", "tenant_id": tenant_id, "total_events": 42, "error_rate": 0.07},
        {"report_id": "failed-payments", "tenant_id": tenant_id, "total_events": 3, "error_rate": 0.33},
    ]
    return rows[: max(1, min(limit, len(rows)))]
