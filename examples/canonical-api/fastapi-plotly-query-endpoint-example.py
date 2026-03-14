from __future__ import annotations

from collections import defaultdict
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

    def fingerprint(self) -> str:
        return "|".join(f"{name}={','.join(values)}" for name, values in self.to_dict().items())


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


def build_chart_payload(state: QueryState) -> dict[str, object]:
    rows = filter_rows(state)
    buckets: dict[str, int] = defaultdict(int)
    total_events = 0
    for row in rows:
        day = str(row["day"])
        events = int(row["events"])
        buckets[day] += events
        total_events += events

    x_values = sorted(buckets)
    y_values = [buckets[day] for day in x_values]
    return {
        "filters": state.to_dict(),
        "query_fingerprint": state.fingerprint(),
        "result_count": len(rows),
        "totals": {"events": total_events},
        "plotly": {
            "data": [
                {
                    "type": "bar",
                    "name": "matching reports",
                    "x": x_values,
                    "y": y_values,
                }
            ],
            "layout": {
                "title": "Live report volume",
                "yaxis": {"title": "Events"},
                "xaxis": {"title": "Day"},
            },
        },
    }


@router.get("/chart")
def report_chart(
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
    return build_chart_payload(state)
