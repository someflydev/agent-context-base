from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse


app = FastAPI()

TENANT_REPORTS = {
    "acme": [
        {"report_id": "daily-signups", "total_events": 42, "status": "ready"},
    ],
    "globex": [
        {"report_id": "ops-latency", "total_events": 17, "status": "warming"},
    ],
}

CHART_SERIES = {
    "signups": [
        {"x": "2026-03-01", "y": 18},
        {"x": "2026-03-02", "y": 24},
        {"x": "2026-03-03", "y": 31},
    ],
}


def get_reports(tenant_id: str, limit: int) -> list[dict[str, object]]:
    return TENANT_REPORTS.get(tenant_id, TENANT_REPORTS["acme"])[:limit]


def get_series(metric: str) -> list[dict[str, object]]:
    return CHART_SERIES.get(metric, CHART_SERIES["signups"])


def render_report_card(tenant_id: str, report: dict[str, object]) -> str:
    total_events = report["total_events"]
    status = report["status"]
    return (
        f'<section id="report-card-{tenant_id}" class="report-card" hx-swap-oob="true">'
        f"<strong>Tenant {tenant_id}</strong>"
        f"<span>{total_events} events</span>"
        f"<small>Status: {status}</small>"
        "</section>"
    )


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "fastapi-uv-example"}


@app.get("/api/reports/{tenant_id}")
async def api_reports(
    tenant_id: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict[str, object]:
    reports = get_reports(tenant_id, limit)
    return {"service": "fastapi-uv-example", "tenant_id": tenant_id, "reports": reports}


@app.get("/fragments/report-card/{tenant_id}")
async def fragment_report_card(tenant_id: str) -> HTMLResponse:
    reports = get_reports(tenant_id, limit=1)
    report = reports[0] if reports else {"report_id": "none", "total_events": 0, "status": "unknown"}
    return HTMLResponse(render_report_card(tenant_id, report))


@app.get("/data/chart/{metric}")
async def data_chart(metric: str) -> dict[str, object]:
    points = get_series(metric)
    return {"metric": metric, "series": [{"name": metric, "points": points}]}
