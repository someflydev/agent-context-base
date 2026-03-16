# crystal-kemal-avram-faceted-filter-example.cr
#
# Demonstrates the full split include/exclude filter panel pattern with Crystal + Kemal.
# Uses inline data; Avram DB queries are not required for this example.
#
# Multi-value params: env.request.query_params.fetch_all("status_out") returns Array(String).

require "kemal"

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

record ReportRow,
  report_id : String,
  team : String,
  status : String,
  region : String,
  events : Int32

REPORT_ROWS = [
  ReportRow.new("daily-signups",     "growth",   "active",   "us",   12),
  ReportRow.new("trial-conversions", "growth",   "active",   "us",   7),
  ReportRow.new("api-latency",       "platform", "paused",   "eu",   5),
  ReportRow.new("checkout-failures", "growth",   "active",   "eu",   9),
  ReportRow.new("queue-depth",       "platform", "active",   "apac", 11),
  ReportRow.new("legacy-import",     "platform", "archived", "us",   4),
]

FACET_OPTIONS = {
  "team"   => ["growth", "platform"],
  "status" => ["active", "paused", "archived"],
  "region" => ["us", "eu", "apac"],
}

QUICK_EXCLUDES = [{"status", "archived"}, {"status", "paused"}]

# ---------------------------------------------------------------------------
# Query state
# ---------------------------------------------------------------------------

record QueryState,
  team_in : Array(String),
  team_out : Array(String),
  status_in : Array(String),
  status_out : Array(String),
  region_in : Array(String),
  region_out : Array(String)

def normalize(values : Array(String)) : Array(String)
  values.map(&.strip.downcase).reject(&.empty?).uniq.sort
end

def build_query_state(env : HTTP::Server::Context) : QueryState
  qp = env.request.query_params
  QueryState.new(
    team_in:    normalize(qp.fetch_all("team_in")),
    team_out:   normalize(qp.fetch_all("team_out")),
    status_in:  normalize(qp.fetch_all("status_in")),
    status_out: normalize(qp.fetch_all("status_out")),
    region_in:  normalize(qp.fetch_all("region_in")),
    region_out: normalize(qp.fetch_all("region_out")),
  )
end

def fingerprint(state : QueryState) : String
  "team_in=#{state.team_in.join(",")}|team_out=#{state.team_out.join(",")}|" \
  "status_in=#{state.status_in.join(",")}|status_out=#{state.status_out.join(",")}|" \
  "region_in=#{state.region_in.join(",")}|region_out=#{state.region_out.join(",")}"
end

# ---------------------------------------------------------------------------
# Filter helpers
# ---------------------------------------------------------------------------

def matches_dim?(value : String, includes : Array(String), excludes : Array(String)) : Bool
  (includes.empty? || includes.includes?(value)) &&
  (excludes.empty? || !excludes.includes?(value))
end

def row_dim_value(row : ReportRow, dim : String) : String
  case dim
  when "team"   then row.team
  when "status" then row.status
  when "region" then row.region
  else               ""
  end
end

def filter_rows(state : QueryState) : Array(ReportRow)
  REPORT_ROWS.select do |row|
    matches_dim?(row.team,   state.team_in,   state.team_out)   &&
    matches_dim?(row.status, state.status_in, state.status_out) &&
    matches_dim?(row.region, state.region_in, state.region_out)
  end
end

def facet_counts(state : QueryState, dimension : String) : Hash(String, Int32)
  options = FACET_OPTIONS[dimension]? || [] of String
  counts  = options.each_with_object({} of String => Int32) { |o, h| h[o] = 0 }

  REPORT_ROWS.each do |row|
    pass = case dimension
    when "team"
      matches_dim?(row.status, state.status_in, state.status_out) &&
      matches_dim?(row.region, state.region_in, state.region_out) &&
      matches_dim?(row.team,   [] of String,    state.team_out)
    when "status"
      matches_dim?(row.team,   state.team_in,   state.team_out)   &&
      matches_dim?(row.region, state.region_in, state.region_out) &&
      matches_dim?(row.status, [] of String,    state.status_out)
    else
      matches_dim?(row.team,   state.team_in,   state.team_out)   &&
      matches_dim?(row.status, state.status_in, state.status_out) &&
      matches_dim?(row.region, [] of String,    state.region_out)
    end
    if pass
      val = row_dim_value(row, dimension)
      counts[val] = (counts[val]? || 0) + 1 if counts.has_key?(val)
    end
  end
  counts
end

def exclude_impact_counts(state : QueryState, dimension : String) : Hash(String, Int32)
  options = FACET_OPTIONS[dimension]? || [] of String
  dim_out = case dimension
  when "team"   then state.team_out
  when "status" then state.status_out
  else               state.region_out
  end

  options.each_with_object({} of String => Int32) do |option, counts|
    other_excludes = dim_out.reject { |v| v == option }
    count = REPORT_ROWS.count do |row|
      val = row_dim_value(row, dimension)
      other_pass = case dimension
      when "team"
        matches_dim?(row.status, state.status_in, state.status_out) &&
        matches_dim?(row.region, state.region_in, state.region_out)
      when "status"
        matches_dim?(row.team,   state.team_in,   state.team_out) &&
        matches_dim?(row.region, state.region_in, state.region_out)
      else
        matches_dim?(row.team,   state.team_in,   state.team_out) &&
        matches_dim?(row.status, state.status_in, state.status_out)
      end
      other_pass &&
      (other_excludes.empty? || !other_excludes.includes?(val)) &&
      val == option
    end
    counts[option] = count
  end
end

# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_filter_panel(state : QueryState) : String
  String.build do |io|
    io << %(<div id="filter-panel" class="space-y-4">)
    io << %(<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>)

    # Quick excludes strip
    io << %(<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">)
    io << %(<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>)
    QUICK_EXCLUDES.each do |dim, val|
      impact   = exclude_impact_counts(state, dim)
      dim_out  = dim == "status" ? state.status_out : dim == "team" ? state.team_out : state.region_out
      is_active = dim_out.includes?(val)
      active_str = is_active ? "true" : "false"
      checked    = is_active ? " checked" : ""
      cls = is_active ?
        "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer" :
        "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
      io << %(<label data-role="quick-exclude" data-quick-exclude-dimension="#{dim}" data-quick-exclude-value="#{val}" data-active="#{active_str}" class="#{cls}">)
      io << %(<input type="checkbox" name="#{dim}_out" value="#{val}"#{checked} class="sr-only" />)
      io << %(#{val.capitalize} <span class="rounded bg-slate-100 px-1 ml-1">#{impact[val]? || 0}</span></label>)
    end
    io << %(</div>)

    # Per-dimension groups
    ["team", "status", "region"].each do |dim|
      inc_counts = facet_counts(state, dim)
      exc_counts = exclude_impact_counts(state, dim)
      dim_out    = dim == "team" ? state.team_out : dim == "status" ? state.status_out : state.region_out
      dim_in     = dim == "team" ? state.team_in  : dim == "status" ? state.status_in  : state.region_in
      options    = FACET_OPTIONS[dim]? || [] of String

      io << %(<section data-filter-dimension="#{dim}" class="space-y-2">)
      io << %(<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">#{dim.capitalize}</h3>)

      # Include sub-section
      io << %(<div data-role="include-options" class="space-y-1">)
      io << %(<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>)
      options.each do |option|
        is_excluded  = dim_out.includes?(option)
        is_checked   = dim_in.includes?(option)
        opt_count    = is_excluded ? 0 : (inc_counts[option]? || 0)
        excluded_attr = is_excluded ? %( data-excluded="true") : ""
        disabled_attr = is_excluded ? " disabled" : ""
        checked_attr  = is_checked  ? " checked"  : ""
        label_extra   = is_excluded ? " opacity-50 cursor-not-allowed" : ""
        io << %(<label data-filter-dimension="#{dim}" data-filter-option="#{option}" data-filter-mode="include" data-option-count="#{opt_count}"#{excluded_attr} class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm#{label_extra}">)
        io << %(<span class="flex items-center gap-2"><input type="checkbox" name="#{dim}_in" value="#{option}"#{checked_attr}#{disabled_attr} /><span class="font-medium text-slate-800">#{option.capitalize}</span></span>)
        io << %(<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">#{opt_count}</span></label>)
      end
      io << %(</div>)

      # Exclude sub-section
      io << %(<div data-role="exclude-options" class="mt-2 space-y-1">)
      io << %(<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>)
      options.each do |option|
        is_active   = dim_out.includes?(option)
        impact      = exc_counts[option]? || 0
        active_attr = is_active ? %( data-active="true") : ""
        checked_attr = is_active ? " checked" : ""
        border_cls   = is_active ? "border-red-200 bg-red-50" : "border-slate-200"
        io << %(<label data-filter-dimension="#{dim}" data-filter-option="#{option}" data-filter-mode="exclude" data-option-count="#{impact}"#{active_attr} class="flex items-center justify-between rounded border #{border_cls} px-3 py-2 text-sm">)
        io << %(<span class="flex items-center gap-2"><input type="checkbox" name="#{dim}_out" value="#{option}"#{checked_attr} /><span class="font-medium text-slate-800">#{option.capitalize}</span></span>)
        io << %(<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">#{impact}</span></label>)
      end
      io << %(</div>)
      io << %(</section>)
    end
    io << %(</div>)
  end
end

def render_results_fragment(state : QueryState) : String
  rows = filter_rows(state)
  n    = rows.size
  fp   = fingerprint(state)
  String.build do |io|
    io << %(<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="#{n}" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">#{n} results</div>)
    io << %(<section id="report-results" data-query-fingerprint="#{fp}" data-result-count="#{n}" class="space-y-2">)
    io << %(<div data-role="active-filters" class="text-xs text-slate-500">#{fp}</div>)
    rows.each do |row|
      io << %(<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="#{row.report_id}"><strong>#{row.report_id}</strong> <span class="text-slate-500">#{row.team} / #{row.status} / #{row.region}</span></div>)
    end
    io << %(</section>)
  end
end

def render_full_page(state : QueryState) : String
  panel = render_filter_panel(state)
  rows  = filter_rows(state)
  n     = rows.size
  fp    = fingerprint(state)
  String.build do |io|
    io << %(<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Reports</title>)
    io << %(<script src="https://unpkg.com/htmx.org@1.9.10"></script>)
    io << %(<script src="https://cdn.tailwindcss.com"></script></head>)
    io << %(<body class="p-6 font-sans"><h1 class="text-xl font-bold mb-4">Reports</h1>)
    io << %(<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">)
    io << %(<div class="flex gap-6"><aside class="w-64 shrink-0">#{panel}</aside><main class="flex-1">)
    io << %(<div id="result-count" data-role="result-count" data-result-count="#{n}" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">#{n} results</div>)
    io << %(<section id="report-results" data-query-fingerprint="#{fp}" data-result-count="#{n}" class="space-y-2">)
    rows.each { |row| io << %(<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="#{row.report_id}"><strong>#{row.report_id}</strong></div>) }
    io << %(</section></main></div></form></body></html>)
  end
end

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

get "/ui/reports" do |env|
  state = build_query_state(env)
  env.response.content_type = "text/html; charset=utf-8"
  render_full_page(state)
end

get "/ui/reports/results" do |env|
  state = build_query_state(env)
  env.response.content_type = "text/html; charset=utf-8"
  render_results_fragment(state)
end

get "/ui/reports/filter-panel" do |env|
  state = build_query_state(env)
  env.response.content_type = "text/html; charset=utf-8"
  render_filter_panel(state)
end

get "/healthz" do |env|
  env.response.content_type = "application/json"
  %({"status":"ok"})
end

Kemal.run
