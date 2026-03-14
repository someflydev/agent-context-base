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

FACET_OPTIONS = {
    "team": ["growth", "platform"],
    "status": ["active", "paused", "archived"],
    "region": ["us", "eu", "apac"],
}


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


def facet_counts(state: QueryState, dimension: str) -> dict[str, int]:
    if dimension not in FACET_OPTIONS:
        raise KeyError(dimension)

    if dimension == "team":
        rows = [
            row
            for row in REPORT_ROWS
            if matches(row, "status", state.status_in, state.status_out)
            and matches(row, "region", state.region_in, state.region_out)
            and matches(row, "team", [], state.team_out)
        ]
    elif dimension == "status":
        rows = [
            row
            for row in REPORT_ROWS
            if matches(row, "team", state.team_in, state.team_out)
            and matches(row, "region", state.region_in, state.region_out)
            and matches(row, "status", [], state.status_out)
        ]
    else:
        rows = [
            row
            for row in REPORT_ROWS
            if matches(row, "team", state.team_in, state.team_out)
            and matches(row, "status", state.status_in, state.status_out)
            and matches(row, "region", [], state.region_out)
        ]

    counts = {option: 0 for option in FACET_OPTIONS[dimension]}
    for row in rows:
        counts[str(row[dimension]).lower()] += 1
    return counts


def render_filter_panel(state: QueryState) -> str:
    sections: list[str] = []
    for dimension in ("team", "status", "region"):
        options = []
        counts = facet_counts(state, dimension)
        for option in FACET_OPTIONS[dimension]:
            options.append(
                f'<button type="button" class="flex w-full items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm" '
                f'data-filter-option="{option}" data-option-count="{counts[option]}" data-filter-mode="include">'
                f'<span class="font-medium text-slate-800">{option}</span>'
                f'<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{counts[option]}</span>'
                "</button>"
            )
        sections.append(
            f'<section data-filter-dimension="{dimension}" class="space-y-2">'
            f'<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">{dimension}</h3>'
            + "".join(options)
            + "</section>"
        )
    return (
        '<div id="filter-panel" class="space-y-4" hx-swap-oob="true">'
        '<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">'
        "Counts reflect the active backend query semantics."
        "</div>"
        + "".join(sections)
        + "</div>"
    )


@router.get("/filter-panel")
def filter_panel(
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
    return HTMLResponse(render_filter_panel(state))
