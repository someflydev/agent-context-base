from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse


app = FastAPI()

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

# Preconfigured quick excludes for the strip at the top of the filter panel.
# Declared as a constant — not auto-derived from data.
QUICK_EXCLUDES: list[tuple[str, str]] = [("status", "archived"), ("status", "paused")]


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


def facet_counts(state: QueryState, dimension: str) -> dict[str, int]:
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


def exclude_impact_counts(state: QueryState, dimension: str) -> dict[str, int]:
    """RULE 2: For each value in dimension, count rows this exclusion removes.

    Apply all other dimensions' filters fully. Apply current dimension's excludes
    except the value being counted. Do not apply current dimension's includes.
    """
    dim_out = getattr(state, f"{dimension}_out")
    counts: dict[str, int] = {}
    for option in FACET_OPTIONS[dimension]:
        other_excludes = [v for v in dim_out if v != option]
        n = 0
        for row in REPORT_ROWS:
            if dimension != "team" and not matches(row, "team", state.team_in, state.team_out):
                continue
            if dimension != "status" and not matches(row, "status", state.status_in, state.status_out):
                continue
            if dimension != "region" and not matches(row, "region", state.region_in, state.region_out):
                continue
            if other_excludes and str(row[dimension]).lower() in other_excludes:
                continue
            if str(row[dimension]).lower() == option:
                n += 1
        counts[option] = n
    return counts


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
            "data": [{"type": "bar", "name": "matching reports", "x": x_values, "y": y_values}],
            "layout": {"title": "Live report volume", "yaxis": {"title": "Events"}, "xaxis": {"title": "Day"}},
        },
    }


def render_result_count_badge(result_count: int, *, oob: bool) -> str:
    oob_attr = ' hx-swap-oob="true"' if oob else ""
    return (
        f'<div id="result-count"{oob_attr} data-role="result-count" data-result-count="{result_count}" '
        'class="inline-flex rounded-full bg-slate-900 px-3 py-1 text-sm font-semibold text-white">'
        f"{result_count} results"
        "</div>"
    )


def render_results_section_html(state: QueryState) -> str:
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
        f'<section id="report-results" class="space-y-4" data-query-fingerprint="{state.fingerprint()}" data-result-count="{len(rows)}">'
        f'<div class="rounded bg-slate-50 px-4 py-3 text-sm text-slate-700" data-role="active-filters">{state.active_filters_label()}</div>'
        f'<div class="grid gap-3 md:grid-cols-2">{cards or empty_state}</div>'
        "</section>"
    )


def render_results_fragment_html(state: QueryState) -> str:
    result_count = len(filter_rows(state))
    return render_result_count_badge(result_count, oob=True) + render_results_section_html(state)


def render_filter_panel_html(state: QueryState) -> str:
    parts: list[str] = []
    parts.append('<div id="filter-panel" class="space-y-4">')
    parts.append(
        '<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">'
        "Counts reflect the active backend query semantics."
        "</div>"
    )

    # Quick excludes strip
    quick_parts: list[str] = []
    for dim, val in QUICK_EXCLUDES:
        impact = exclude_impact_counts(state, dim)
        is_active = val in getattr(state, f"{dim}_out")
        active_val = "true" if is_active else "false"
        if is_active:
            label_cls = (
                "flex items-center gap-1 rounded border border-red-300 bg-red-50 "
                "px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
            )
            badge_cls = "rounded bg-red-100 px-1 ml-1"
            prefix = "\u2715 "
        else:
            label_cls = (
                "flex items-center gap-1 rounded border border-slate-200 "
                "px-2 py-1 text-xs text-slate-600 hover:border-slate-400 cursor-pointer"
            )
            badge_cls = "rounded bg-slate-100 px-1 ml-1"
            prefix = ""
        checked_attr = " checked" if is_active else ""
        quick_parts.append(
            f'<label data-role="quick-exclude" data-quick-exclude-dimension="{dim}" '
            f'data-quick-exclude-value="{val}" data-active="{active_val}" '
            f'class="{label_cls}">'
            f'<input type="checkbox" name="{dim}_out" value="{val}"{checked_attr} class="sr-only" />'
            f"{prefix}{val.title()}"
            f'<span class="{badge_cls}">{impact[val]}</span>'
            f"</label>"
        )
    parts.append(
        '<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" '
        'data-role="quick-excludes-strip">'
        '<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">'
        "Quick excludes</span>"
        + "".join(quick_parts)
        + "</div>"
    )

    # Per-dimension groups with split include/exclude sub-sections
    for dimension in ("team", "status", "region"):
        inc_counts = facet_counts(state, dimension)
        exc_counts = exclude_impact_counts(state, dimension)
        dim_out: list[str] = getattr(state, f"{dimension}_out")
        dim_in: list[str] = getattr(state, f"{dimension}_in")

        # Include sub-section
        inc_options: list[str] = []
        for option in FACET_OPTIONS[dimension]:
            is_excluded = option in dim_out
            is_checked = option in dim_in
            # RULE 1: force count to 0 when value is excluded
            opt_count = 0 if is_excluded else inc_counts[option]
            excluded_attr = ' data-excluded="true"' if is_excluded else ""
            disabled_attr = " disabled" if is_excluded else ""
            checked_attr = " checked" if is_checked else ""
            label_extra = " opacity-50 cursor-not-allowed" if is_excluded else ""
            inc_options.append(
                f'<label data-filter-dimension="{dimension}" data-filter-option="{option}" '
                f'data-filter-mode="include" data-option-count="{opt_count}"{excluded_attr} '
                f'class="flex items-center justify-between rounded border border-slate-200 '
                f'px-3 py-2 text-sm{label_extra}">'
                f'<span class="flex items-center gap-2">'
                f'<input type="checkbox" name="{dimension}_in" value="{option}"{checked_attr}{disabled_attr} />'
                f'<span class="font-medium text-slate-800">{option.title()}</span>'
                f"</span>"
                f'<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">'
                f"{opt_count}</span>"
                f"</label>"
            )

        # Exclude sub-section
        exc_options: list[str] = []
        for option in FACET_OPTIONS[dimension]:
            is_active = option in dim_out
            opt_count = exc_counts[option]
            active_attr = ' data-active="true"' if is_active else ""
            checked_attr = " checked" if is_active else ""
            border_cls = "border-red-200 bg-red-50" if is_active else "border-slate-200"
            exc_options.append(
                f'<label data-filter-dimension="{dimension}" data-filter-option="{option}" '
                f'data-filter-mode="exclude" data-option-count="{opt_count}"{active_attr} '
                f'class="flex items-center justify-between rounded border {border_cls} '
                f'px-3 py-2 text-sm">'
                f'<span class="flex items-center gap-2">'
                f'<input type="checkbox" name="{dimension}_out" value="{option}"{checked_attr} />'
                f'<span class="font-medium text-slate-800">{option.title()}</span>'
                f"</span>"
                f'<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">'
                f"{opt_count}</span>"
                f"</label>"
            )

        parts.append(
            f'<section data-filter-dimension="{dimension}" class="space-y-2">'
            f'<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">{dimension}</h3>'
            f'<div class="space-y-1">'
            f'<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>'
            + "".join(inc_options)
            + "</div>"
            f'<div class="mt-2 space-y-1">'
            f'<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>'
            + "".join(exc_options)
            + "</div>"
            + "</section>"
        )

    parts.append("</div>")
    return "".join(parts)


def render_dashboard_page(state: QueryState) -> str:
    result_count = len(filter_rows(state))
    return (
        '<!doctype html><html><head><meta charset="utf-8"><title>Backend-driven reports</title></head>'
        + '<body class="min-h-screen bg-slate-100 text-slate-900">'
        + '<main class="mx-auto max-w-6xl space-y-6 px-6 py-10">'
        + '<header class="space-y-2">'
        + '<p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">HTMX + Tailwind + Plotly</p>'
        + '<h1 class="text-3xl font-semibold">Report query console</h1>'
        + '</header>'
        + '<form id="report-filters" class="grid gap-6 lg:grid-cols-[320px,1fr]" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">'
        + '<aside class="rounded-2xl bg-white p-5 shadow-sm">'
        + render_filter_panel_html(state)
        + '</aside>'
        + '<section class="space-y-4">'
        + '<div class="flex items-center justify-between">'
        + '<div class="space-y-1">'
        + '<p class="text-xs uppercase tracking-wide text-slate-500">Live query state</p>'
        + f'<div class="text-sm text-slate-700" data-role="query-fingerprint">{state.fingerprint()}</div>'
        + '</div>'
        + render_result_count_badge(result_count, oob=False)
        + '</div>'
        + '<div id="report-chart" class="rounded-2xl bg-white p-5 shadow-sm" data-plotly-endpoint="/api/reports/chart" data-query-fingerprint="' + state.fingerprint() + '">'
        + '<div class="text-sm font-medium text-slate-800">Plotly chart target</div>'
        + '<div class="mt-2 text-xs text-slate-500">Fetch /api/reports/chart with the same query state and call Plotly.react.</div>'
        + '</div>'
        + render_results_section_html(state)
        + '</section>'
        + '</form>'
        + '</main></body></html>'
    )


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


@app.get("/ui/reports")
def ui_reports(
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
    return HTMLResponse(render_dashboard_page(state))


@app.get("/ui/reports/results")
def ui_report_results(
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
    return HTMLResponse(render_results_fragment_html(state))


@app.get("/ui/reports/filter-panel")
def ui_filter_panel(
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
    return HTMLResponse(render_filter_panel_html(state))


@app.get("/api/reports/chart")
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
