from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/reports", tags=["reports"])

REPORT_ROWS = [
    {"report_id": "daily-signups", "team": "growth", "status": "active", "region": "us", "day": "2026-03-01", "events": 12},
    {"report_id": "trial-conversions", "team": "growth", "status": "active", "region": "us", "day": "2026-03-02", "events": 7},
    {"report_id": "api-latency", "team": "platform", "status": "paused", "region": "eu", "day": "2026-03-01", "events": 5},
    {"report_id": "checkout-failures", "team": "growth", "status": "active", "region": "eu", "day": "2026-03-03", "events": 9},
    {"report_id": "queue-depth", "team": "platform", "status": "active", "region": "apac", "day": "2026-03-02", "events": 11},
    {"report_id": "legacy-import", "team": "platform", "status": "archived", "region": "us", "day": "2026-03-01", "events": 4},
]


def normalize(values: list[str] | None) -> list[str]:
    return sorted({value.strip().lower() for value in (values or []) if value and value.strip()})


@dataclass(slots=True)
class QueryState:
    team_in: list[str]
    team_out: list[str]
    status_in: list[str]
    status_out: list[str]
    region_in: list[str]
    region_out: list[str]

    def fingerprint(self) -> str:
        parts = [
            ("team_in", self.team_in),
            ("team_out", self.team_out),
            ("status_in", self.status_in),
            ("status_out", self.status_out),
            ("region_in", self.region_in),
            ("region_out", self.region_out),
        ]
        return "|".join(f"{name}={','.join(values)}" for name, values in parts)

    def active_filters_label(self) -> str:
        labels: list[str] = []
        if self.team_in:
            labels.append(f"team in {', '.join(self.team_in)}")
        if self.team_out:
            labels.append(f"team not {', '.join(self.team_out)}")
        if self.status_in:
            labels.append(f"status in {', '.join(self.status_in)}")
        if self.status_out:
            labels.append(f"status not {', '.join(self.status_out)}")
        if self.region_in:
            labels.append(f"region in {', '.join(self.region_in)}")
        if self.region_out:
            labels.append(f"region not {', '.join(self.region_out)}")
        return " | ".join(labels) if labels else "all reports"


def build_query_state(
    *,
    team_in: list[str] | None = None,
    team_out: list[str] | None = None,
    status_in: list[str] | None = None,
    status_out: list[str] | None = None,
    region_in: list[str] | None = None,
    region_out: list[str] | None = None,
) -> QueryState:
    return QueryState(
        team_in=normalize(team_in),
        team_out=normalize(team_out),
        status_in=normalize(status_in),
        status_out=normalize(status_out),
        region_in=normalize(region_in),
        region_out=normalize(region_out),
    )


def matches(row: dict[str, object], field: str, includes: list[str], excludes: list[str]) -> bool:
    value = str(row[field]).lower()
    if includes and value not in includes:
        return False
    if excludes and value in excludes:
        return False
    return True


def filter_rows(state: QueryState) -> list[dict[str, object]]:
    return [
        dict(row)
        for row in REPORT_ROWS
        if matches(row, "team", state.team_in, state.team_out)
        and matches(row, "status", state.status_in, state.status_out)
        and matches(row, "region", state.region_in, state.region_out)
    ]


def render_results_fragment(state: QueryState) -> str:
    rows = filter_rows(state)
    empty_state = '<div class="rounded border border-dashed border-slate-300 p-4 text-sm text-slate-500">No matching reports.</div>'
    cards = "".join(
        f'<article class="rounded border border-slate-200 bg-white p-4 shadow-sm" data-report-id="{row["report_id"]}">'
        f'<div class="text-sm font-semibold text-slate-900">{row["report_id"]}</div>'
        f'<div class="mt-1 text-xs uppercase tracking-wide text-slate-500">{row["team"]} · {row["status"]} · {row["region"]}</div>'
        f'<div class="mt-3 text-sm text-slate-700">{row["events"]} events</div>'
        "</article>"
        for row in rows
    )
    return (
        f'<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="{len(rows)}" '
        'class="inline-flex rounded-full bg-slate-900 px-3 py-1 text-sm font-semibold text-white">'
        f"{len(rows)} results"
        "</div>"
        f'<section id="report-results" class="space-y-4" data-query-fingerprint="{state.fingerprint()}" data-result-count="{len(rows)}">'
        f'<div class="rounded bg-slate-50 px-4 py-3 text-sm text-slate-700" data-role="active-filters">{state.active_filters_label()}</div>'
        f'<div class="grid gap-3 md:grid-cols-2">{cards or empty_state}</div>'
        "</section>"
    )


@router.get("/results")
def report_results(
    team_in: list[str] | None = Query(default=None),
    team_out: list[str] | None = Query(default=None),
    status_in: list[str] | None = Query(default=None),
    status_out: list[str] | None = Query(default=None),
    region_in: list[str] | None = Query(default=None),
    region_out: list[str] | None = Query(default=None),
) -> HTMLResponse:
    state = build_query_state(
        team_in=team_in,
        team_out=team_out,
        status_in=status_in,
        status_out=status_out,
        region_in=region_in,
        region_out=region_out,
    )
    return HTMLResponse(render_results_fragment(state))
