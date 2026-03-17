//! rust-axum-faceted-filter-example.rs
//!
//! Demonstrates the full split include/exclude filter panel pattern with Rust + Axum.
//! HTML is built as String using push_str/format!. A real app would use maud or askama.
//!
//! Multi-value params: FilterQuery uses Vec<String> with #[serde(default)].
//! Axum's Query<T> extractor natively handles ?status_out=archived&status_out=paused
//! into Vec<String> when serde is configured with default.

use axum::{
    extract::Query,
    response::Html,
    routing::get,
    Router,
};
use serde::Deserialize;
use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Dataset
// ---------------------------------------------------------------------------

struct ReportRow {
    report_id: &'static str,
    team: &'static str,
    status: &'static str,
    region: &'static str,
    events: u32,
}

static REPORT_ROWS: &[ReportRow] = &[
    ReportRow { report_id: "daily-signups",     team: "growth",   status: "active",   region: "us",   events: 12 },
    ReportRow { report_id: "trial-conversions", team: "growth",   status: "active",   region: "us",   events: 7  },
    ReportRow { report_id: "api-latency",       team: "platform", status: "paused",   region: "eu",   events: 5  },
    ReportRow { report_id: "checkout-failures", team: "growth",   status: "active",   region: "eu",   events: 9  },
    ReportRow { report_id: "queue-depth",       team: "platform", status: "active",   region: "apac", events: 11 },
    ReportRow { report_id: "legacy-import",     team: "platform", status: "archived", region: "us",   events: 4  },
];

fn facet_option_list(dimension: &str) -> &'static [&'static str] {
    match dimension {
        "team"   => &["growth", "platform"],
        "status" => &["active", "paused", "archived"],
        "region" => &["us", "eu", "apac"],
        _        => &[],
    }
}

static QUICK_EXCLUDES: &[(&str, &str)] = &[("status", "archived"), ("status", "paused")];

static VALID_SORT_VALUES: &[&str] = &["events_desc", "events_asc", "name_asc"];

// ---------------------------------------------------------------------------
// Query state
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, Default)]
pub struct FilterQuery {
    #[serde(default)] pub team_in:    Vec<String>,
    #[serde(default)] pub team_out:   Vec<String>,
    #[serde(default)] pub status_in:  Vec<String>,
    #[serde(default)] pub status_out: Vec<String>,
    #[serde(default)] pub region_in:  Vec<String>,
    #[serde(default)] pub region_out: Vec<String>,
    #[serde(default)] pub query:      String,
    #[serde(default)] pub sort:       String,
}

#[derive(Debug, Clone, Default)]
pub struct QueryState {
    pub team_in:    Vec<String>,
    pub team_out:   Vec<String>,
    pub status_in:  Vec<String>,
    pub status_out: Vec<String>,
    pub region_in:  Vec<String>,
    pub region_out: Vec<String>,
    pub query:      String,
    pub sort:       String,
}

fn normalize(values: Vec<String>) -> Vec<String> {
    let mut set: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    for v in values {
        let s = v.trim().to_lowercase();
        if !s.is_empty() {
            set.insert(s);
        }
    }
    set.into_iter().collect()
}

fn normalize_sort(s: String) -> String {
    if VALID_SORT_VALUES.contains(&s.as_str()) {
        s
    } else {
        "events_desc".to_string()
    }
}

fn build_query_state(q: FilterQuery) -> QueryState {
    QueryState {
        team_in:    normalize(q.team_in),
        team_out:   normalize(q.team_out),
        status_in:  normalize(q.status_in),
        status_out: normalize(q.status_out),
        region_in:  normalize(q.region_in),
        region_out: normalize(q.region_out),
        query:      q.query.trim().to_lowercase(),
        sort:       normalize_sort(q.sort),
    }
}

fn fingerprint(state: &QueryState) -> String {
    format!(
        "team_in={}|team_out={}|status_in={}|status_out={}|region_in={}|region_out={}|query={}|sort={}",
        state.team_in.join(","),
        state.team_out.join(","),
        state.status_in.join(","),
        state.status_out.join(","),
        state.region_in.join(","),
        state.region_out.join(","),
        state.query,
        state.sort,
    )
}

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

fn matches_dim(value: &str, includes: &[String], excludes: &[String]) -> bool {
    if !includes.is_empty() && !includes.iter().any(|v| v == value) {
        return false;
    }
    if !excludes.is_empty() && excludes.iter().any(|v| v == value) {
        return false;
    }
    true
}

fn row_dim_value<'a>(row: &'a ReportRow, dim: &str) -> &'a str {
    match dim {
        "team"   => row.team,
        "status" => row.status,
        "region" => row.region,
        _        => "",
    }
}

fn apply_text_search<'a>(rows: &'a [ReportRow], q: &str) -> Vec<&'a ReportRow> {
    if q.is_empty() {
        return rows.iter().collect();
    }
    rows.iter().filter(|row| row.report_id.to_lowercase().contains(q)).collect()
}

fn sort_rows(rows: &mut Vec<&'static ReportRow>, sort_val: &str) {
    match sort_val {
        "events_asc" => rows.sort_by(|a, b| {
            a.events.cmp(&b.events).then_with(|| a.report_id.cmp(b.report_id))
        }),
        "name_asc" => rows.sort_by(|a, b| a.report_id.cmp(b.report_id)),
        _ => rows.sort_by(|a, b| {
            b.events.cmp(&a.events).then_with(|| a.report_id.cmp(b.report_id))
        }),
    }
}

fn filter_rows(state: &QueryState) -> Vec<&'static ReportRow> {
    let searched = apply_text_search(REPORT_ROWS, &state.query);
    searched.into_iter().filter(|row| {
        matches_dim(row.team,   &state.team_in,   &state.team_out)   &&
        matches_dim(row.status, &state.status_in, &state.status_out) &&
        matches_dim(row.region, &state.region_in, &state.region_out)
    }).collect()
}

fn facet_counts(state: &QueryState, dimension: &str) -> HashMap<&'static str, usize> {
    let options = facet_option_list(dimension);
    let mut counts: HashMap<&'static str, usize> = options.iter().map(|&o| (o, 0)).collect();

    let searched = apply_text_search(REPORT_ROWS, &state.query);
    for row in searched.iter() {
        let pass = match dimension {
            "team" =>
                matches_dim(row.status, &state.status_in, &state.status_out) &&
                matches_dim(row.region, &state.region_in, &state.region_out) &&
                matches_dim(row.team,   &[],              &state.team_out),
            "status" =>
                matches_dim(row.team,   &state.team_in,   &state.team_out)   &&
                matches_dim(row.region, &state.region_in, &state.region_out) &&
                matches_dim(row.status, &[],              &state.status_out),
            _ =>
                matches_dim(row.team,   &state.team_in,   &state.team_out)   &&
                matches_dim(row.status, &state.status_in, &state.status_out) &&
                matches_dim(row.region, &[],              &state.region_out),
        };
        if pass {
            let val = row_dim_value(row, dimension);
            if let Some(c) = counts.get_mut(val) {
                *c += 1;
            }
        }
    }
    counts
}

fn exclude_impact_counts(state: &QueryState, dimension: &str) -> HashMap<&'static str, usize> {
    let options = facet_option_list(dimension);
    let dim_out: &[String] = match dimension {
        "team"   => &state.team_out,
        "status" => &state.status_out,
        _        => &state.region_out,
    };

    let searched = apply_text_search(REPORT_ROWS, &state.query);
    let mut counts = HashMap::new();
    for &option in options.iter() {
        let other_excludes: Vec<&String> = dim_out.iter().filter(|v| v.as_str() != option).collect();
        let mut count = 0usize;
        for row in searched.iter() {
            let other_pass = match dimension {
                "team" =>
                    matches_dim(row.status, &state.status_in, &state.status_out) &&
                    matches_dim(row.region, &state.region_in, &state.region_out),
                "status" =>
                    matches_dim(row.team,   &state.team_in,   &state.team_out)   &&
                    matches_dim(row.region, &state.region_in, &state.region_out),
                _ =>
                    matches_dim(row.team,   &state.team_in,   &state.team_out)   &&
                    matches_dim(row.status, &state.status_in, &state.status_out),
            };
            let val = row_dim_value(row, dimension);
            let not_other_excluded = other_excludes.is_empty() ||
                !other_excludes.iter().any(|v| v.as_str() == val);
            if other_pass && not_other_excluded && val == option {
                count += 1;
            }
        }
        counts.insert(option, count);
    }
    counts
}

// ---------------------------------------------------------------------------
// HTML rendering
// ---------------------------------------------------------------------------

fn capitalize(s: &str) -> String {
    let mut c = s.chars();
    match c.next() {
        None => String::new(),
        Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
    }
}

fn render_search_input(state: &QueryState) -> String {
    format!(
        r#"<input type="text" name="query" value="{}" placeholder="Search reports…" data-role="search-input" data-search-query="{}" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="keyup changed delay:300ms" hx-include="#report-filters" class="w-full rounded border border-slate-300 px-3 py-2 text-sm" />"#,
        state.query, state.query,
    )
}

fn render_sort_select(state: &QueryState) -> String {
    let sel_desc = if state.sort == "events_desc" { " selected" } else { "" };
    let sel_asc  = if state.sort == "events_asc"  { " selected" } else { "" };
    let sel_name = if state.sort == "name_asc"    { " selected" } else { "" };
    format!(
        r#"<select name="sort" data-role="sort-select" data-sort-order="{}" hx-get="/ui/reports/results" hx-target="#report-results" hx-include="#report-filters" class="rounded border border-slate-200 px-2 py-1 text-sm"><option value="events_desc"{}> Events: high → low</option><option value="events_asc"{}> Events: low → high</option><option value="name_asc"{}> Name: A → Z</option></select>"#,
        state.sort, sel_desc, sel_asc, sel_name,
    )
}

fn render_filter_panel(state: &QueryState) -> String {
    let mut html = String::new();

    html.push_str(r#"<div id="filter-panel" class="space-y-4">"#);
    html.push_str(r#"<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>"#);

    // Search input
    html.push_str(&render_search_input(state));

    // Quick excludes strip
    html.push_str(r#"<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">"#);
    html.push_str(r#"<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>"#);
    for &(dim, val) in QUICK_EXCLUDES.iter() {
        let impact   = exclude_impact_counts(state, dim);
        let dim_out: &[String] = match dim { "status" => &state.status_out, "team" => &state.team_out, _ => &state.region_out };
        let is_active = dim_out.iter().any(|v| v == val);
        let active_str = if is_active { "true" } else { "false" };
        let checked    = if is_active { " checked" } else { "" };
        let cls = if is_active {
            "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
        } else {
            "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
        };
        html.push_str(&format!(
            r#"<label data-role="quick-exclude" data-quick-exclude-dimension="{}" data-quick-exclude-value="{}" data-active="{}" class="{}">"#,
            dim, val, active_str, cls,
        ));
        html.push_str(&format!(
            r#"<input type="checkbox" name="{}_out" value="{}"{} class="sr-only" />"#,
            dim, val, checked,
        ));
        html.push_str(&format!(
            r#"{} <span class="rounded bg-slate-100 px-1 ml-1">{}</span></label>"#,
            capitalize(val), impact.get(val).unwrap_or(&0),
        ));
    }
    html.push_str("</div>");

    // Per-dimension groups
    for dim in &["team", "status", "region"] {
        let inc_counts = facet_counts(state, dim);
        let exc_counts = exclude_impact_counts(state, dim);
        let dim_out: &[String] = match *dim { "team" => &state.team_out, "status" => &state.status_out, _ => &state.region_out };
        let dim_in:  &[String] = match *dim { "team" => &state.team_in,  "status" => &state.status_in,  _ => &state.region_in  };
        let options = facet_option_list(dim);

        html.push_str(&format!(r#"<section data-filter-dimension="{}" class="space-y-2">"#, dim));
        html.push_str(&format!(r#"<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">{}</h3>"#, capitalize(dim)));

        // Include sub-section
        html.push_str(r#"<div data-role="include-options" class="space-y-1">"#);
        html.push_str(r#"<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>"#);
        for &option in options.iter() {
            let is_excluded  = dim_out.iter().any(|v| v == option);
            let is_checked   = dim_in.iter().any(|v| v == option);
            let opt_count    = if is_excluded { 0 } else { *inc_counts.get(option).unwrap_or(&0) };
            let excluded_attr = if is_excluded { r#" data-excluded="true""# } else { "" };
            let disabled_attr = if is_excluded { " disabled" } else { "" };
            let checked_attr  = if is_checked  { " checked"  } else { "" };
            let label_extra   = if is_excluded { " opacity-50 cursor-not-allowed" } else { "" };
            html.push_str(&format!(
                r#"<label data-filter-dimension="{}" data-filter-option="{}" data-filter-mode="include" data-option-count="{}"{} class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm{}">"#,
                dim, option, opt_count, excluded_attr, label_extra,
            ));
            html.push_str(r#"<span class="flex items-center gap-2">"#);
            html.push_str(&format!(
                r#"<input type="checkbox" name="{}_in" value="{}"{}{} />"#,
                dim, option, checked_attr, disabled_attr,
            ));
            html.push_str(&format!(r#"<span class="font-medium text-slate-800">{}</span></span>"#, capitalize(option)));
            html.push_str(&format!(r#"<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{}</span></label>"#, opt_count));
        }
        html.push_str("</div>");

        // Exclude sub-section
        html.push_str(r#"<div data-role="exclude-options" class="mt-2 space-y-1">"#);
        html.push_str(r#"<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>"#);
        for &option in options.iter() {
            let is_active  = dim_out.iter().any(|v| v == option);
            let impact     = *exc_counts.get(option).unwrap_or(&0);
            let active_attr = if is_active { r#" data-active="true""# } else { "" };
            let checked_attr = if is_active { " checked" } else { "" };
            let border_cls   = if is_active { "border-red-200 bg-red-50" } else { "border-slate-200" };
            html.push_str(&format!(
                r#"<label data-filter-dimension="{}" data-filter-option="{}" data-filter-mode="exclude" data-option-count="{}"{} class="flex items-center justify-between rounded border {} px-3 py-2 text-sm">"#,
                dim, option, impact, active_attr, border_cls,
            ));
            html.push_str(r#"<span class="flex items-center gap-2">"#);
            html.push_str(&format!(r#"<input type="checkbox" name="{}_out" value="{}"{}  />"#, dim, option, checked_attr));
            html.push_str(&format!(r#"<span class="font-medium text-slate-800">{}</span></span>"#, capitalize(option)));
            html.push_str(&format!(r#"<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{}</span></label>"#, impact));
        }
        html.push_str("</div>");
        html.push_str("</section>");
    }

    html.push_str("</div>");
    html
}

fn render_results_fragment(state: &QueryState) -> String {
    let mut rows = filter_rows(state);
    sort_rows(&mut rows, &state.sort);
    let n    = rows.len();
    let fp   = fingerprint(state);
    let sort_select = render_sort_select(state);
    let mut html = String::new();

    html.push_str(&format!(
        r#"<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="{}" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">{} results</div>"#,
        n, n,
    ));
    html.push_str(&format!(
        r#"<section id="report-results" data-query-fingerprint="{}" data-result-count="{}" data-search-query="{}" data-sort-order="{}" class="space-y-2">"#,
        fp, n, state.query, state.sort,
    ));
    html.push_str(&format!(r#"<div data-role="active-filters" class="text-xs text-slate-500">{}</div>"#, fp));
    html.push_str(&sort_select);
    for row in rows.iter() {
        html.push_str(&format!(
            r#"<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="{}"><strong>{}</strong> <span class="text-slate-500">{} / {} / {}</span></div>"#,
            row.report_id, row.report_id, row.team, row.status, row.region,
        ));
    }
    html.push_str("</section>");
    html
}

fn render_full_page(state: &QueryState) -> String {
    let panel       = render_filter_panel(state);
    let mut rows    = filter_rows(state);
    sort_rows(&mut rows, &state.sort);
    let n           = rows.len();
    let fp          = fingerprint(state);
    let sort_select = render_sort_select(state);
    let cards = rows.iter().map(|row| format!(
        r#"<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="{}"><strong>{}</strong></div>"#,
        row.report_id, row.report_id,
    )).collect::<Vec<_>>().join("\n");

    format!(r#"<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Reports</title>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="font-sans">
<h1 class="text-xl font-bold p-4">Reports</h1>
<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">
<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">
<aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">{}</aside>
<main id="report-results-container" class="flex-1 overflow-y-auto p-4">
<div id="result-count" data-role="result-count" data-result-count="{}" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">{} results</div>
{}
<section id="report-results" data-query-fingerprint="{}" data-result-count="{}" data-search-query="{}" data-sort-order="{}" class="space-y-2 mt-3">
{}
</section>
</main></div></form></body></html>"#,
        panel, n, n, sort_select, fp, n, state.query, state.sort, cards,
    )
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

async fn ui_reports(Query(q): Query<FilterQuery>) -> Html<String> {
    let state = build_query_state(q);
    Html(render_full_page(&state))
}

async fn ui_reports_results(Query(q): Query<FilterQuery>) -> Html<String> {
    let state = build_query_state(q);
    Html(render_results_fragment(&state))
}

async fn ui_reports_filter_panel(Query(q): Query<FilterQuery>) -> Html<String> {
    let state = build_query_state(q);
    Html(render_filter_panel(&state))
}

async fn healthz() -> &'static str {
    r#"{"status":"ok"}"#
}

pub fn router() -> Router {
    Router::new()
        .route("/ui/reports",              get(ui_reports))
        .route("/ui/reports/results",      get(ui_reports_results))
        .route("/ui/reports/filter-panel", get(ui_reports_filter_panel))
        .route("/healthz",                 get(healthz))
}

#[tokio::main]
async fn main() {
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, router()).await.unwrap();
}
