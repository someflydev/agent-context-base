"""
fastapi-search-sort-filter-example.py

Extends the split include/exclude filter panel pattern with three PROMPT_64 features:

  FEATURE A — Text search bar (RULE 4):
    apply_text_search(rows, query) narrows the row set before any facet logic runs.
    Searches case-insensitive substring match on report_id.
    facet_counts and exclude_impact_counts both call apply_text_search first.
    The search input carries name="query", data-role="search-input",
    data-search-query, and hx-trigger="keyup changed delay:300ms".

  FEATURE B — Sort order (RULE 5):
    sort_rows(rows, sort_value) sorts the result list only — never affects counts.
    Three options: events_desc (default), events_asc, name_asc.
    The sort select carries name="sort", data-role="sort-select", data-sort-order.
    Pre-selected option prevents the dropdown from resetting on HTMX swaps.

  FEATURE C — Independent scroll layout (RULE 6):
    CSS-only. flex h-screen overflow-hidden wrapper + overflow-y-auto on each column.
    Layout wrapper is NOT a partial swap target; only id="report-results" is swapped.

Uses the same REPORT_ROWS, FACET_OPTIONS, and QUICK_EXCLUDES as other canonical examples.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse


app = FastAPI()

# ── Dataset (shared across all canonical examples) ────────────────────────────

REPORT_ROWS = [
    {"report_id": "daily-signups",     "team": "growth",   "status": "active",   "region": "us",   "events": 12},
    {"report_id": "trial-conversions", "team": "growth",   "status": "active",   "region": "us",   "events": 7},
    {"report_id": "api-latency",       "team": "platform", "status": "paused",   "region": "eu",   "events": 5},
    {"report_id": "checkout-failures", "team": "growth",   "status": "active",   "region": "eu",   "events": 9},
    {"report_id": "queue-depth",       "team": "platform", "status": "active",   "region": "apac", "events": 11},
    {"report_id": "legacy-import",     "team": "platform", "status": "archived", "region": "us",   "events": 4},
]

FACET_OPTIONS: dict[str, list[str]] = {
    "team": ["growth", "platform"],
    "status": ["active", "paused", "archived"],
    "region": ["us", "eu", "apac"],
}

QUICK_EXCLUDES: list[tuple[str, str]] = [("status", "archived"), ("status", "paused")]

SORT_OPTIONS: list[tuple[str, str]] = [
    ("events_desc", "Events: high \u2192 low"),
    ("events_asc",  "Events: low \u2192 high"),
    ("name_asc",    "Name: A \u2192 Z"),
]

VALID_SORT_VALUES = {v for v, _ in SORT_OPTIONS}


# ── Query state ───────────────────────────────────────────────────────────────

def normalize(values: list[str] | None) -> list[str]:
    return sorted({v.strip().lower() for v in (values or []) if v and v.strip()})


def normalize_query(q: str | None) -> str:
    return (q or "").strip().lower()


def normalize_sort(s: str | None) -> str:
    v = (s or "").strip().lower()
    return v if v in VALID_SORT_VALUES else "events_desc"


@dataclass(slots=True)
class QueryState:
    team_in: list[str]
    team_out: list[str]
    status_in: list[str]
    status_out: list[str]
    region_in: list[str]
    region_out: list[str]
    query: str
    sort: str

    def fingerprint(self) -> str:
        return (
            f"team_in={','.join(self.team_in)}"
            f"|team_out={','.join(self.team_out)}"
            f"|status_in={','.join(self.status_in)}"
            f"|status_out={','.join(self.status_out)}"
            f"|region_in={','.join(self.region_in)}"
            f"|region_out={','.join(self.region_out)}"
            f"|query={self.query}"
            f"|sort={self.sort}"
        )


def build_query_state(
    *,
    team_in: list[str] | None = None,
    team_out: list[str] | None = None,
    status_in: list[str] | None = None,
    status_out: list[str] | None = None,
    region_in: list[str] | None = None,
    region_out: list[str] | None = None,
    query: str | None = None,
    sort: str | None = None,
) -> QueryState:
    return QueryState(
        team_in=normalize(team_in),
        team_out=normalize(team_out),
        status_in=normalize(status_in),
        status_out=normalize(status_out),
        region_in=normalize(region_in),
        region_out=normalize(region_out),
        query=normalize_query(query),
        sort=normalize_sort(sort),
    )


# ── Text search helper (RULE 4) ───────────────────────────────────────────────

def apply_text_search(rows: list[dict], query: str) -> list[dict]:
    """Filter rows by case-insensitive substring match on report_id.

    This is a base filter applied before any facet dimension logic runs.
    Q is never relaxed — apply it first in filter_rows, facet_counts, and
    exclude_impact_counts.

    Searches report_id only. Returns all rows when query is empty.
    """
    if not query:
        return rows
    return [r for r in rows if query in r["report_id"].lower()]


# ── Sort helper (RULE 5) ──────────────────────────────────────────────────────

def sort_rows(rows: list[dict], sort_value: str) -> list[dict]:
    """Sort result rows by the given sort value.

    sort_value meanings:
      "events_desc" → numeric descending by events (tiebreak: report_id asc)
      "events_asc"  → numeric ascending by events  (tiebreak: report_id asc)
      "name_asc"    → lexicographic ascending by report_id

    Sort never affects counts. Only call this when building the result list.
    """
    if sort_value == "events_asc":
        return sorted(rows, key=lambda r: (r["events"], r["report_id"]))
    if sort_value == "name_asc":
        return sorted(rows, key=lambda r: r["report_id"])
    # Default: events_desc
    return sorted(rows, key=lambda r: (-r["events"], r["report_id"]))


# ── Query helpers ─────────────────────────────────────────────────────────────

def matches(row: dict, field: str, includes: list[str], excludes: list[str]) -> bool:
    value = str(row[field]).lower()
    if includes and value not in includes:
        return False
    if excludes and value in excludes:
        return False
    return True


def filter_rows(state: QueryState) -> list[dict]:
    """Apply text search first, then dimension filters."""
    rows = apply_text_search(REPORT_ROWS, state.query)
    return [
        dict(row)
        for row in rows
        if matches(row, "team", state.team_in, state.team_out)
        and matches(row, "status", state.status_in, state.status_out)
        and matches(row, "region", state.region_in, state.region_out)
    ]


def facet_counts(state: QueryState, dimension: str) -> dict[str, int]:
    """Include counts: apply text search first, then other dims, relax same-dim includes."""
    # RULE 4b: apply text search before facet count relaxation — Q is never relaxed.
    base = apply_text_search(REPORT_ROWS, state.query)
    if dimension == "team":
        rows = [
            row for row in base
            if matches(row, "status", state.status_in, state.status_out)
            and matches(row, "region", state.region_in, state.region_out)
            and matches(row, "team", [], state.team_out)
        ]
    elif dimension == "status":
        rows = [
            row for row in base
            if matches(row, "team", state.team_in, state.team_out)
            and matches(row, "region", state.region_in, state.region_out)
            and matches(row, "status", [], state.status_out)
        ]
    else:
        rows = [
            row for row in base
            if matches(row, "team", state.team_in, state.team_out)
            and matches(row, "status", state.status_in, state.status_out)
            and matches(row, "region", [], state.region_out)
        ]
    counts = {option: 0 for option in FACET_OPTIONS[dimension]}
    for row in rows:
        counts[str(row[dimension]).lower()] += 1
    return counts


def exclude_impact_counts(state: QueryState, dimension: str) -> dict[str, int]:
    """RULE 4c: apply text search first, then other-dimension filters, count per value.

    Computation:
      1. Apply Q (text search) — never relaxed.
      2. Apply all _in/_out for all OTHER dimensions fully.
      3. Apply dimension's D_out EXCEPT the value being counted.
      4. Do NOT apply dimension's D_in.
      5. Count rows where row[dimension] == value.
    """
    # RULE 4c: apply text search first.
    base = apply_text_search(REPORT_ROWS, state.query)
    dim_out = getattr(state, f"{dimension}_out")
    counts: dict[str, int] = {}
    for option in FACET_OPTIONS[dimension]:
        other_excludes = [v for v in dim_out if v != option]
        n = 0
        for row in base:
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


# ── Filter panel rendering ────────────────────────────────────────────────────

def _render_quick_excludes(state: QueryState) -> str:
    parts: list[str] = []
    for dim, val in QUICK_EXCLUDES:
        impact = exclude_impact_counts(state, dim)
        is_active = val in getattr(state, f"{dim}_out")
        active_val = "true" if is_active else "false"
        checked_attr = " checked" if is_active else ""
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
        parts.append(
            f'<label data-role="quick-exclude" data-quick-exclude-dimension="{dim}" '
            f'data-quick-exclude-value="{val}" data-active="{active_val}" '
            f'class="{label_cls}">'
            f'<input type="checkbox" name="{dim}_out" value="{val}"{checked_attr} class="sr-only" />'
            f"{prefix}{val.title()}"
            f'<span class="{badge_cls}">{impact[val]}</span>'
            f"</label>"
        )
    return (
        '<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" '
        'data-role="quick-excludes-strip">'
        '<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">'
        "Quick excludes</span>"
        + "".join(parts)
        + "</div>"
    )


def _render_dimension_groups(state: QueryState) -> str:
    parts: list[str] = []
    for dimension in ("team", "status", "region"):
        inc_counts = facet_counts(state, dimension)
        exc_counts = exclude_impact_counts(state, dimension)
        dim_out: list[str] = getattr(state, f"{dimension}_out")
        dim_in: list[str] = getattr(state, f"{dimension}_in")

        inc_options: list[str] = []
        for option in FACET_OPTIONS[dimension]:
            is_excluded = option in dim_out
            is_checked = option in dim_in
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
            f'<div data-role="include-options" class="space-y-1">'
            f'<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>'
            + "".join(inc_options)
            + "</div>"
            f'<div data-role="exclude-options" class="mt-2 space-y-1">'
            f'<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>'
            + "".join(exc_options)
            + "</div>"
            + "</section>"
        )
    return "".join(parts)


def _render_search_input(state: QueryState) -> str:
    """RULE 4g: search input with required data-* attributes and debounced trigger."""
    q = state.query
    return (
        f'<input type="text" name="query" value="{q}" placeholder="Search reports\u2026" '
        f'data-role="search-input" data-search-query="{q}" '
        f'hx-get="/ui/reports/results" hx-target="#report-results" '
        f'hx-trigger="keyup changed delay:300ms" hx-include="#report-filters" '
        f'class="w-full rounded border border-slate-300 px-3 py-2 text-sm '
        f'placeholder:text-slate-400 focus:border-blue-400 focus:outline-none" />'
    )


def _render_sort_select(state: QueryState) -> str:
    """RULE 5c: sort select with data-role, data-sort-order, and correct selected option."""
    options_html = ""
    for val, label in SORT_OPTIONS:
        selected = " selected" if state.sort == val else ""
        options_html += f'<option value="{val}"{selected}>{label}</option>'
    return (
        f'<select name="sort" data-role="sort-select" data-sort-order="{state.sort}" '
        f'hx-get="/ui/reports/results" hx-target="#report-results" '
        f'hx-include="#report-filters" '
        f'class="rounded border border-slate-200 px-2 py-1 text-sm text-slate-700">'
        + options_html
        + "</select>"
    )


def render_filter_panel_fragment(state: QueryState) -> str:
    """Filter panel fragment. Includes search input at the top.

    Used by the /ui/reports/filter-panel endpoint when only the panel needs
    refreshing without touching the results section.
    """
    search_input = _render_search_input(state)
    quick_strip = _render_quick_excludes(state)
    dim_groups = _render_dimension_groups(state)
    return (
        '<div id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4 space-y-4">'
        '<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">'
        "Counts reflect the active backend query semantics."
        "</div>"
        + search_input
        + quick_strip
        + dim_groups
        + "</div>"
    )


def render_results_fragment(state: QueryState) -> str:
    """HTMX partial: OOB result-count badge + results section with sort select and cards.

    RULE 4d: result-count badge reflects rows passing both Q and all facet filters.
    RULE 5b: sort select pre-populated so it does not reset on HTMX swaps.
    New data-* on results section: data-search-query, data-sort-order.
    """
    filtered = filter_rows(state)
    sorted_rows = sort_rows(filtered, state.sort)
    n = len(filtered)
    fp = state.fingerprint()

    cards = "".join(
        f'<div class="rounded border border-slate-200 px-4 py-3 text-sm" '
        f'data-report-id="{row["report_id"]}">'
        f'<strong>{row["report_id"]}</strong> '
        f'<span class="ml-2 text-slate-500">{row["team"]} / {row["status"]} / {row["region"]}'
        f' &bull; events: {row["events"]}</span>'
        f"</div>"
        for row in sorted_rows
    )

    sort_select = _render_sort_select(state)

    return (
        f'<div id="result-count" hx-swap-oob="true" '
        f'data-role="result-count" data-result-count="{n}" '
        f'class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">'
        f"{n} results</div>"
        f'<section id="report-results" '
        f'data-query-fingerprint="{fp}" '
        f'data-result-count="{n}" '
        f'data-search-query="{state.query}" '
        f'data-sort-order="{state.sort}" '
        f'class="space-y-2">'
        f'<div class="flex items-center justify-between mb-2">'
        f'<div data-role="active-filters" class="text-xs text-slate-500">{fp}</div>'
        + sort_select
        + "</div>"
        + cards
        + "</section>"
    )


def render_full_page(state: QueryState) -> str:
    """RULE 6: independent scroll layout with h-screen overflow-hidden wrapper.

    Layout wrapper is NOT a partial swap target — only id="report-results" is swapped.
    The HTMX form wraps both the filter panel and results container so that all inputs
    (including search and sort) are included in partial update requests.
    """
    filtered = filter_rows(state)
    sorted_rows = sort_rows(filtered, state.sort)
    n = len(filtered)
    fp = state.fingerprint()

    filter_panel_inner = (
        '<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">'
        "Counts reflect the active backend query semantics.</div>"
        + _render_search_input(state)
        + _render_quick_excludes(state)
        + _render_dimension_groups(state)
    )

    cards = "".join(
        f'<div class="rounded border border-slate-200 px-4 py-3 text-sm" '
        f'data-report-id="{row["report_id"]}">'
        f'<strong>{row["report_id"]}</strong> '
        f'<span class="ml-2 text-slate-500">{row["team"]} / {row["status"]} / {row["region"]}'
        f' &bull; events: {row["events"]}</span>'
        f"</div>"
        for row in sorted_rows
    )

    sort_select = _render_sort_select(state)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Reports</title>
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <form id="report-filters"
        hx-get="/ui/reports/results"
        hx-target="#report-results"
        hx-trigger="change, submit">
    <!-- RULE 6: data-role="reports-layout" — flex h-screen overflow-hidden, NOT a swap target -->
    <div data-role="reports-layout"
         id="reports-layout"
         class="flex h-screen overflow-hidden">

      <!-- Filter panel: fixed width, independent vertical scroll -->
      <aside id="filter-panel"
             class="w-72 flex-shrink-0 overflow-y-auto border-r p-4 space-y-4">
        {filter_panel_inner}
      </aside>

      <!-- Results container: remaining width, independent vertical scroll -->
      <main id="report-results-container"
            class="flex-1 overflow-y-auto p-4">
        <div class="flex items-center justify-between mb-3">
          <div id="result-count"
               data-role="result-count"
               data-result-count="{n}"
               class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
            {n} results
          </div>
          {sort_select}
        </div>
        <!-- id="report-results" is the HTMX swap target -->
        <section id="report-results"
                 data-query-fingerprint="{fp}"
                 data-result-count="{n}"
                 data-search-query="{state.query}"
                 data-sort-order="{state.sort}"
                 class="space-y-2">
          <div data-role="active-filters" class="text-xs text-slate-500">{fp}</div>
          {cards}
        </section>
      </main>
    </div>
  </form>
</body>
</html>"""


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/ui/reports")
def ui_reports(
    team_in: list[str] | None = Query(default=None),
    team_out: list[str] | None = Query(default=None),
    status_in: list[str] | None = Query(default=None),
    status_out: list[str] | None = Query(default=None),
    region_in: list[str] | None = Query(default=None),
    region_out: list[str] | None = Query(default=None),
    query: str | None = Query(default=None),
    sort: str | None = Query(default=None),
) -> HTMLResponse:
    state = build_query_state(
        team_in=team_in, team_out=team_out,
        status_in=status_in, status_out=status_out,
        region_in=region_in, region_out=region_out,
        query=query, sort=sort,
    )
    return HTMLResponse(render_full_page(state))


@app.get("/ui/reports/results")
def ui_reports_results(
    team_in: list[str] | None = Query(default=None),
    team_out: list[str] | None = Query(default=None),
    status_in: list[str] | None = Query(default=None),
    status_out: list[str] | None = Query(default=None),
    region_in: list[str] | None = Query(default=None),
    region_out: list[str] | None = Query(default=None),
    query: str | None = Query(default=None),
    sort: str | None = Query(default=None),
) -> HTMLResponse:
    state = build_query_state(
        team_in=team_in, team_out=team_out,
        status_in=status_in, status_out=status_out,
        region_in=region_in, region_out=region_out,
        query=query, sort=sort,
    )
    return HTMLResponse(render_results_fragment(state))


@app.get("/ui/reports/filter-panel")
def ui_reports_filter_panel(
    team_in: list[str] | None = Query(default=None),
    team_out: list[str] | None = Query(default=None),
    status_in: list[str] | None = Query(default=None),
    status_out: list[str] | None = Query(default=None),
    region_in: list[str] | None = Query(default=None),
    region_out: list[str] | None = Query(default=None),
    query: str | None = Query(default=None),
    sort: str | None = Query(default=None),
) -> HTMLResponse:
    state = build_query_state(
        team_in=team_in, team_out=team_out,
        status_in=status_in, status_out=status_out,
        region_in=region_in, region_out=region_out,
        query=query, sort=sort,
    )
    return HTMLResponse(render_filter_panel_fragment(state))


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
