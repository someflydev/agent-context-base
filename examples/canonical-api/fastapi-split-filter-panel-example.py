"""
fastapi-split-filter-panel-example.py

Demonstrates the full split include/exclude filter panel rendering pattern:
  - QUICK_EXCLUDES constant for the preconfigured quick-exclude strip
  - exclude_impact_counts(state, dimension) implementing RULE 2
  - render_split_filter_panel(state) producing a complete HTML fragment with:
      * quick-excludes strip at the top
      * per-dimension groups with include and exclude sub-sections
      * RULE 1: include option for excluded value shows count=0, greyed, disabled
      * RULE 2: exclude option shows exclude impact count
      * RULE 3: quick exclude toggles mirror main section exclude state
      * all required data-* attributes on every option element

Uses the same REPORT_ROWS and FACET_OPTIONS dataset as other canonical examples.
QUICK_EXCLUDES: [("status", "archived"), ("status", "paused")]
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse


app = FastAPI()

# ── Dataset (shared across all canonical examples) ────────────────────────────

REPORT_ROWS = [
    {"report_id": "daily-signups", "team": "growth", "status": "active", "region": "us", "day": "2026-03-01", "events": 12},
    {"report_id": "trial-conversions", "team": "growth", "status": "active", "region": "us", "day": "2026-03-02", "events": 7},
    {"report_id": "api-latency", "team": "platform", "status": "paused", "region": "eu", "day": "2026-03-01", "events": 5},
    {"report_id": "checkout-failures", "team": "growth", "status": "active", "region": "eu", "day": "2026-03-03", "events": 9},
    {"report_id": "queue-depth", "team": "platform", "status": "active", "region": "apac", "day": "2026-03-02", "events": 11},
    {"report_id": "legacy-import", "team": "platform", "status": "archived", "region": "us", "day": "2026-03-01", "events": 4},
]

FACET_OPTIONS: dict[str, list[str]] = {
    "team": ["growth", "platform"],
    "status": ["active", "paused", "archived"],
    "region": ["us", "eu", "apac"],
}

# Two quick excludes in the same dimension group — demonstrates the strip pattern.
QUICK_EXCLUDES: list[tuple[str, str]] = [("status", "archived"), ("status", "paused")]


# ── Query state ───────────────────────────────────────────────────────────────

def normalize(values: list[str] | None) -> list[str]:
    return sorted({v.strip().lower() for v in (values or []) if v and v.strip()})


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
        return "|".join(f"{k}={','.join(v)}" for k, v in self.to_dict().items())


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


# ── Query helpers ─────────────────────────────────────────────────────────────

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
    """Include counts: all other dimensions active; current dimension's includes relaxed."""
    if dimension == "team":
        rows = [
            row for row in REPORT_ROWS
            if matches(row, "status", state.status_in, state.status_out)
            and matches(row, "region", state.region_in, state.region_out)
            and matches(row, "team", [], state.team_out)
        ]
    elif dimension == "status":
        rows = [
            row for row in REPORT_ROWS
            if matches(row, "team", state.team_in, state.team_out)
            and matches(row, "region", state.region_in, state.region_out)
            and matches(row, "status", [], state.status_out)
        ]
    else:
        rows = [
            row for row in REPORT_ROWS
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

    Computation:
      1. Apply all _in/_out for all OTHER dimensions fully.
      2. Apply dimension's D_out EXCEPT the value being counted.
      3. Do NOT apply dimension's D_in.
      4. Count rows where row[dimension] == value.

    When the value is already in D_out this answers "how many rows is it removing?"
    When the value is not in D_out this is a preview "how many would it remove?"
    """
    dim_out = getattr(state, f"{dimension}_out")
    counts: dict[str, int] = {}
    for option in FACET_OPTIONS[dimension]:
        other_excludes = [v for v in dim_out if v != option]
        n = 0
        for row in REPORT_ROWS:
            # Other dimensions: apply fully
            if dimension != "team" and not matches(row, "team", state.team_in, state.team_out):
                continue
            if dimension != "status" and not matches(row, "status", state.status_in, state.status_out):
                continue
            if dimension != "region" and not matches(row, "region", state.region_in, state.region_out):
                continue
            # Current dimension: apply other excludes only (not the value being counted)
            if other_excludes and str(row[dimension]).lower() in other_excludes:
                continue
            # Count rows where this dimension equals the option
            if str(row[dimension]).lower() == option:
                n += 1
        counts[option] = n
    return counts


# ── Filter panel rendering ────────────────────────────────────────────────────

def render_split_filter_panel(state: QueryState) -> str:
    """Render a complete split include/exclude filter panel fragment.

    Emits:
      - quick-excludes strip (from QUICK_EXCLUDES constant)
      - per-dimension groups with include sub-section and exclude sub-section
      - all required data-* attributes for Playwright verification
    """
    parts: list[str] = []
    parts.append('<div id="filter-panel" class="space-y-4">')
    parts.append(
        '<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">'
        "Counts reflect the active backend query semantics."
        "</div>"
    )

    # ── Quick excludes strip ──────────────────────────────────────────────────
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

    # ── Per-dimension groups ──────────────────────────────────────────────────
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
            # RULE 1: short-circuit count to 0 for excluded values
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


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.get("/ui/reports/split-filter-panel")
def ui_split_filter_panel(
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
    return HTMLResponse(render_split_filter_panel(state))
