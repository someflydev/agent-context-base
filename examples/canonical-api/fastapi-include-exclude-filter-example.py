from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Query


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

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "team_in": self.team_in,
            "team_out": self.team_out,
            "status_in": self.status_in,
            "status_out": self.status_out,
            "region_in": self.region_in,
            "region_out": self.region_out,
        }


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


def matches_dimension(row: dict[str, object], field: str, includes: list[str], excludes: list[str]) -> bool:
    value = str(row[field]).lower()
    if includes and value not in includes:
        return False
    if excludes and value in excludes:
        return False
    return True


def filter_rows(state: QueryState) -> list[dict[str, object]]:
    matched: list[dict[str, object]] = []
    for row in REPORT_ROWS:
        if not matches_dimension(row, "team", state.team_in, state.team_out):
            continue
        if not matches_dimension(row, "status", state.status_in, state.status_out):
            continue
        if not matches_dimension(row, "region", state.region_in, state.region_out):
            continue
        matched.append(dict(row))
    return matched


@router.get("/search")
def search_reports(
    team_in: list[str] | None = Query(default=None),
    team_out: list[str] | None = Query(default=None),
    status_in: list[str] | None = Query(default=None),
    status_out: list[str] | None = Query(default=None),
    region_in: list[str] | None = Query(default=None),
    region_out: list[str] | None = Query(default=None),
) -> dict[str, object]:
    state = build_query_state(
        team_in=team_in,
        team_out=team_out,
        status_in=status_in,
        status_out=status_out,
        region_in=region_in,
        region_out=region_out,
    )
    rows = filter_rows(state)
    return {
        "filters": state.to_dict(),
        "result_count": len(rows),
        "items": [{"report_id": row["report_id"], "team": row["team"], "status": row["status"]} for row in rows],
    }
