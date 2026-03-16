// typescript-hono-faceted-filter-example.ts
//
// Demonstrates the full split include/exclude filter panel pattern with TypeScript + Hono + Bun.
// HTML is built as template literal strings and returned via c.html().
//
// Multi-value params: new URL(c.req.url).searchParams.getAll("status_out") returns string[].
// Run with: bun run typescript-hono-faceted-filter-example.ts

import { Hono } from "hono";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type QueryState = {
  team_in: string[];
  team_out: string[];
  status_in: string[];
  status_out: string[];
  region_in: string[];
  region_out: string[];
};

type ReportRow = {
  report_id: string;
  team: string;
  status: string;
  region: string;
  events: number;
};

// ---------------------------------------------------------------------------
// Dataset
// ---------------------------------------------------------------------------

const REPORT_ROWS: ReportRow[] = [
  { report_id: "daily-signups",     team: "growth",   status: "active",   region: "us",   events: 12 },
  { report_id: "trial-conversions", team: "growth",   status: "active",   region: "us",   events: 7  },
  { report_id: "api-latency",       team: "platform", status: "paused",   region: "eu",   events: 5  },
  { report_id: "checkout-failures", team: "growth",   status: "active",   region: "eu",   events: 9  },
  { report_id: "queue-depth",       team: "platform", status: "active",   region: "apac", events: 11 },
  { report_id: "legacy-import",     team: "platform", status: "archived", region: "us",   events: 4  },
];

const FACET_OPTIONS: Record<string, string[]> = {
  team:   ["growth", "platform"],
  status: ["active", "paused", "archived"],
  region: ["us", "eu", "apac"],
};

const QUICK_EXCLUDES: [string, string][] = [
  ["status", "archived"],
  ["status", "paused"],
];

// ---------------------------------------------------------------------------
// Query state
// ---------------------------------------------------------------------------

function normalize(values: string[] | undefined): string[] {
  if (!values || values.length === 0) return [];
  const seen = new Set<string>();
  const result: string[] = [];
  for (const v of values) {
    const s = v.trim().toLowerCase();
    if (s && !seen.has(s)) {
      seen.add(s);
      result.push(s);
    }
  }
  return result.sort();
}

function buildQueryState(searchParams: URLSearchParams): QueryState {
  return {
    team_in:    normalize(searchParams.getAll("team_in")),
    team_out:   normalize(searchParams.getAll("team_out")),
    status_in:  normalize(searchParams.getAll("status_in")),
    status_out: normalize(searchParams.getAll("status_out")),
    region_in:  normalize(searchParams.getAll("region_in")),
    region_out: normalize(searchParams.getAll("region_out")),
  };
}

function fingerprint(state: QueryState): string {
  return [
    `team_in=${state.team_in.join(",")}`,
    `team_out=${state.team_out.join(",")}`,
    `status_in=${state.status_in.join(",")}`,
    `status_out=${state.status_out.join(",")}`,
    `region_in=${state.region_in.join(",")}`,
    `region_out=${state.region_out.join(",")}`,
  ].join("|");
}

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

function matchesDim(value: string, includes: string[], excludes: string[]): boolean {
  if (includes.length > 0 && !includes.includes(value)) return false;
  if (excludes.length > 0 && excludes.includes(value)) return false;
  return true;
}

function filterRows(state: QueryState): ReportRow[] {
  return REPORT_ROWS.filter(row =>
    matchesDim(row.team,   state.team_in,   state.team_out)   &&
    matchesDim(row.status, state.status_in, state.status_out) &&
    matchesDim(row.region, state.region_in, state.region_out)
  );
}

function rowDimValue(row: ReportRow, dim: string): string {
  return (row as Record<string, string | number>)[dim] as string;
}

function facetCounts(state: QueryState, dimension: string): Record<string, number> {
  const options = FACET_OPTIONS[dimension] ?? [];
  const counts: Record<string, number> = Object.fromEntries(options.map(o => [o, 0]));

  for (const row of REPORT_ROWS) {
    let pass = false;
    if (dimension === "team") {
      pass =
        matchesDim(row.status, state.status_in, state.status_out) &&
        matchesDim(row.region, state.region_in, state.region_out) &&
        matchesDim(row.team,   [],              state.team_out);
    } else if (dimension === "status") {
      pass =
        matchesDim(row.team,   state.team_in,   state.team_out)   &&
        matchesDim(row.region, state.region_in, state.region_out) &&
        matchesDim(row.status, [],              state.status_out);
    } else {
      pass =
        matchesDim(row.team,   state.team_in,   state.team_out)   &&
        matchesDim(row.status, state.status_in, state.status_out) &&
        matchesDim(row.region, [],              state.region_out);
    }
    if (pass) {
      const val = rowDimValue(row, dimension);
      if (val in counts) counts[val]++;
    }
  }
  return counts;
}

function excludeImpactCounts(state: QueryState, dimension: string): Record<string, number> {
  const options = FACET_OPTIONS[dimension] ?? [];
  const dimOut: string[] =
    dimension === "team"   ? state.team_out   :
    dimension === "status" ? state.status_out :
                             state.region_out;

  const counts: Record<string, number> = {};
  for (const option of options) {
    const otherExcludes = dimOut.filter(v => v !== option);
    let count = 0;
    for (const row of REPORT_ROWS) {
      let otherPass = false;
      if (dimension === "team") {
        otherPass =
          matchesDim(row.status, state.status_in, state.status_out) &&
          matchesDim(row.region, state.region_in, state.region_out);
      } else if (dimension === "status") {
        otherPass =
          matchesDim(row.team,   state.team_in,   state.team_out)   &&
          matchesDim(row.region, state.region_in, state.region_out);
      } else {
        otherPass =
          matchesDim(row.team,   state.team_in,   state.team_out)   &&
          matchesDim(row.status, state.status_in, state.status_out);
      }
      const val = rowDimValue(row, dimension);
      if (otherPass && (otherExcludes.length === 0 || !otherExcludes.includes(val)) && val === option) {
        count++;
      }
    }
    counts[option] = count;
  }
  return counts;
}

// ---------------------------------------------------------------------------
// HTML rendering
// ---------------------------------------------------------------------------

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function renderFilterPanel(state: QueryState): string {
  const quickStrip = renderQuickExcludes(state);
  const dimGroups  = ["team", "status", "region"].map(dim => renderDimensionGroup(state, dim)).join("\n");

  return `
<div id="filter-panel" class="space-y-4">
  <div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">
    Counts reflect the active backend query semantics.
  </div>
  ${quickStrip}
  ${dimGroups}
</div>`;
}

function renderQuickExcludes(state: QueryState): string {
  const buttons = QUICK_EXCLUDES.map(([dim, val]) => {
    const impact   = excludeImpactCounts(state, dim);
    const dimOut   = dim === "status" ? state.status_out : dim === "team" ? state.team_out : state.region_out;
    const isActive = dimOut.includes(val);
    const activeStr = isActive ? "true" : "false";
    const checked   = isActive ? " checked" : "";
    const cls = isActive
      ? "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
      : "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer";
    return `
    <label data-role="quick-exclude"
           data-quick-exclude-dimension="${dim}"
           data-quick-exclude-value="${val}"
           data-active="${activeStr}"
           class="${cls}">
      <input type="checkbox" name="${dim}_out" value="${val}"${checked} class="sr-only" />
      ${capitalize(val)}
      <span class="rounded bg-slate-100 px-1 ml-1">${impact[val] ?? 0}</span>
    </label>`;
  }).join("");

  return `
  <div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3"
       data-role="quick-excludes-strip">
    <span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>
    ${buttons}
  </div>`;
}

function renderDimensionGroup(state: QueryState, dim: string): string {
  const incCounts = facetCounts(state, dim);
  const excCounts = excludeImpactCounts(state, dim);
  const dimOut    = dim === "team" ? state.team_out   : dim === "status" ? state.status_out : state.region_out;
  const dimIn     = dim === "team" ? state.team_in    : dim === "status" ? state.status_in  : state.region_in;
  const options   = FACET_OPTIONS[dim] ?? [];

  const incOptions = options.map(option => {
    const isExcluded  = dimOut.includes(option);
    const isChecked   = dimIn.includes(option);
    const optCount    = isExcluded ? 0 : (incCounts[option] ?? 0);
    const excludedAttr = isExcluded ? ` data-excluded="true"` : "";
    const disabledAttr = isExcluded ? " disabled" : "";
    const checkedAttr  = isChecked  ? " checked"  : "";
    const labelExtra   = isExcluded ? " opacity-50 cursor-not-allowed" : "";
    return `
      <label data-filter-dimension="${dim}" data-filter-option="${option}"
             data-filter-mode="include" data-option-count="${optCount}"${excludedAttr}
             class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm${labelExtra}">
        <span class="flex items-center gap-2">
          <input type="checkbox" name="${dim}_in" value="${option}"${checkedAttr}${disabledAttr} />
          <span class="font-medium text-slate-800">${capitalize(option)}</span>
        </span>
        <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">${optCount}</span>
      </label>`;
  }).join("");

  const excOptions = options.map(option => {
    const isActive   = dimOut.includes(option);
    const impact     = excCounts[option] ?? 0;
    const activeAttr = isActive ? ` data-active="true"` : "";
    const checkedAttr = isActive ? " checked" : "";
    const borderCls   = isActive ? "border-red-200 bg-red-50" : "border-slate-200";
    return `
      <label data-filter-dimension="${dim}" data-filter-option="${option}"
             data-filter-mode="exclude" data-option-count="${impact}"${activeAttr}
             class="flex items-center justify-between rounded border ${borderCls} px-3 py-2 text-sm">
        <span class="flex items-center gap-2">
          <input type="checkbox" name="${dim}_out" value="${option}"${checkedAttr} />
          <span class="font-medium text-slate-800">${capitalize(option)}</span>
        </span>
        <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">${impact}</span>
      </label>`;
  }).join("");

  return `
  <section data-filter-dimension="${dim}" class="space-y-2">
    <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">${capitalize(dim)}</h3>
    <div data-role="include-options" class="space-y-1">
      <p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>
      ${incOptions}
    </div>
    <div data-role="exclude-options" class="mt-2 space-y-1">
      <p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>
      ${excOptions}
    </div>
  </section>`;
}

function renderResultsFragment(state: QueryState): string {
  const rows = filterRows(state);
  const n    = rows.length;
  const fp   = fingerprint(state);
  const cards = rows.map(r =>
    `<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${r.report_id}">` +
    `<strong>${r.report_id}</strong> <span class="text-slate-500">${r.team} / ${r.status} / ${r.region}</span></div>`
  ).join("\n");

  return `
<div id="result-count" hx-swap-oob="true"
     data-role="result-count" data-result-count="${n}"
     class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
  ${n} results
</div>
<section id="report-results"
         data-query-fingerprint="${fp}"
         data-result-count="${n}"
         class="space-y-2">
  <div data-role="active-filters" class="text-xs text-slate-500">${fp}</div>
  ${cards}
</section>`;
}

function renderFullPage(state: QueryState): string {
  const panel = renderFilterPanel(state);
  const rows  = filterRows(state);
  const n     = rows.length;
  const fp    = fingerprint(state);
  const cards = rows.map(r =>
    `<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${r.report_id}">` +
    `<strong>${r.report_id}</strong></div>`
  ).join("\n");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Reports</title>
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="p-6 font-sans">
  <h1 class="text-xl font-bold mb-4">Reports</h1>
  <form id="report-filters"
        hx-get="/ui/reports/results"
        hx-target="#report-results"
        hx-trigger="change, submit">
    <div class="flex gap-6">
      <aside class="w-64 shrink-0">${panel}</aside>
      <main class="flex-1">
        <div id="result-count"
             data-role="result-count"
             data-result-count="${n}"
             class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">
          ${n} results
        </div>
        <section id="report-results"
                 data-query-fingerprint="${fp}"
                 data-result-count="${n}"
                 class="space-y-2">
          ${cards}
        </section>
      </main>
    </div>
  </form>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

const app = new Hono();

app.get("/ui/reports", async (c) => {
  const state = buildQueryState(new URL(c.req.url).searchParams);
  return c.html(renderFullPage(state));
});

app.get("/ui/reports/results", async (c) => {
  const state = buildQueryState(new URL(c.req.url).searchParams);
  return c.html(renderResultsFragment(state));
});

app.get("/ui/reports/filter-panel", async (c) => {
  const state = buildQueryState(new URL(c.req.url).searchParams);
  return c.html(renderFilterPanel(state));
});

app.get("/healthz", (c) => c.json({ status: "ok" }));

export default app;
