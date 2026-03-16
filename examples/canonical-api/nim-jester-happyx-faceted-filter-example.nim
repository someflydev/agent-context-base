# nim-jester-happyx-faceted-filter-example.nim
#
# Demonstrates the full split include/exclude filter panel pattern with Nim + Jester.
# HTML is built using fmt strings and string concatenation.
#
# Multi-value params: Jester's @"status_out" returns the last single value.
# This example parses multi-value params by splitting the raw query string on '&'.
# A production implementation may use a URL parsing library instead.

import jester, strformat, strutils, sequtils, tables, algorithm, sets

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

type ReportRow = tuple[reportId, team, status, region: string; events: int]

const reportRows: seq[ReportRow] = @[
  ("daily-signups",     "growth",   "active",   "us",   12),
  ("trial-conversions", "growth",   "active",   "us",   7),
  ("api-latency",       "platform", "paused",   "eu",   5),
  ("checkout-failures", "growth",   "active",   "eu",   9),
  ("queue-depth",       "platform", "active",   "apac", 11),
  ("legacy-import",     "platform", "archived", "us",   4),
]

let facetOptions = {
  "team":   @["growth", "platform"],
  "status": @["active", "paused", "archived"],
  "region": @["us", "eu", "apac"],
}.toTable

const quickExcludes = @[("status", "archived"), ("status", "paused")]

# ---------------------------------------------------------------------------
# Query state
# ---------------------------------------------------------------------------

type QueryState = object
  teamIn, teamOut:     seq[string]
  statusIn, statusOut: seq[string]
  regionIn, regionOut: seq[string]

proc normalize(values: seq[string]): seq[string] =
  var seen = initHashSet[string]()
  result = @[]
  for v in values:
    let s = v.strip().toLowerAscii()
    if s.len > 0 and not seen.contains(s):
      seen.incl(s)
      result.add(s)
  result.sort()

proc parseMultiParam(queryStr: string; key: string): seq[string] =
  ## Parse all values for a repeated query parameter from a raw query string.
  ## e.g. "status_out=archived&status_out=paused" → @["archived", "paused"]
  result = @[]
  let qs = queryStr.strip(chars = {'?'})
  for part in qs.split('&'):
    let kv = part.split('=')
    if kv.len == 2 and kv[0] == key:
      result.add(kv[1].decodeUrl())

proc buildQueryState(queryStr: string): QueryState =
  QueryState(
    teamIn:    normalize(parseMultiParam(queryStr, "team_in")),
    teamOut:   normalize(parseMultiParam(queryStr, "team_out")),
    statusIn:  normalize(parseMultiParam(queryStr, "status_in")),
    statusOut: normalize(parseMultiParam(queryStr, "status_out")),
    regionIn:  normalize(parseMultiParam(queryStr, "region_in")),
    regionOut: normalize(parseMultiParam(queryStr, "region_out")),
  )

proc fingerprint(state: QueryState): string =
  fmt"team_in={state.teamIn.join(",")}|team_out={state.teamOut.join(",")}|" &
  fmt"status_in={state.statusIn.join(",")}|status_out={state.statusOut.join(",")}|" &
  fmt"region_in={state.regionIn.join(",")}|region_out={state.regionOut.join(",")}"

# ---------------------------------------------------------------------------
# Filter helpers
# ---------------------------------------------------------------------------

proc matchesDim(value: string; includes, excludes: seq[string]): bool =
  (includes.len == 0 or value in includes) and
  (excludes.len == 0 or value notin excludes)

proc rowDimValue(row: ReportRow; dim: string): string =
  case dim
  of "team":   row.team
  of "status": row.status
  of "region": row.region
  else:        ""

proc filterRows(state: QueryState): seq[ReportRow] =
  for row in reportRows:
    if matchesDim(row.team,   state.teamIn,   state.teamOut)   and
       matchesDim(row.status, state.statusIn, state.statusOut) and
       matchesDim(row.region, state.regionIn, state.regionOut):
      result.add(row)

proc facetCounts(state: QueryState; dimension: string): Table[string, int] =
  let options = facetOptions.getOrDefault(dimension, @[])
  result = initTable[string, int]()
  for o in options: result[o] = 0
  for row in reportRows:
    let pass = case dimension
      of "team":
        matchesDim(row.status, state.statusIn, state.statusOut) and
        matchesDim(row.region, state.regionIn, state.regionOut) and
        matchesDim(row.team,   @[],            state.teamOut)
      of "status":
        matchesDim(row.team,   state.teamIn,   state.teamOut)   and
        matchesDim(row.region, state.regionIn, state.regionOut) and
        matchesDim(row.status, @[],            state.statusOut)
      else:
        matchesDim(row.team,   state.teamIn,   state.teamOut)   and
        matchesDim(row.status, state.statusIn, state.statusOut) and
        matchesDim(row.region, @[],            state.regionOut)
    if pass:
      let v = rowDimValue(row, dimension)
      if result.hasKey(v): result[v] += 1

proc excludeImpactCounts(state: QueryState; dimension: string): Table[string, int] =
  let options = facetOptions.getOrDefault(dimension, @[])
  let dimOut  = case dimension
    of "team":   state.teamOut
    of "status": state.statusOut
    else:        state.regionOut
  result = initTable[string, int]()
  for option in options:
    let otherExcludes = dimOut.filterIt(it != option)
    var count = 0
    for row in reportRows:
      let v = rowDimValue(row, dimension)
      let otherPass = case dimension
        of "team":
          matchesDim(row.status, state.statusIn, state.statusOut) and
          matchesDim(row.region, state.regionIn, state.regionOut)
        of "status":
          matchesDim(row.team,   state.teamIn,   state.teamOut)   and
          matchesDim(row.region, state.regionIn, state.regionOut)
        else:
          matchesDim(row.team,   state.teamIn,   state.teamOut)   and
          matchesDim(row.status, state.statusIn, state.statusOut)
      if otherPass and (otherExcludes.len == 0 or v notin otherExcludes) and v == option:
        count += 1
    result[option] = count

# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

proc capFirst(s: string): string =
  if s.len == 0: return s
  result = s
  result[0] = result[0].toUpperAscii()

proc renderFilterPanel(state: QueryState): string =
  result = ""
  result &= """<div id="filter-panel" class="space-y-4">"""
  result &= """<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>"""

  # Quick excludes strip
  result &= """<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">"""
  result &= """<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>"""
  for (dim, val) in quickExcludes:
    let impact   = excludeImpactCounts(state, dim)
    let dimOut   = case dim
      of "status": state.statusOut
      of "team":   state.teamOut
      else:        state.regionOut
    let isActive  = val in dimOut
    let activeStr = if isActive: "true" else: "false"
    let checked   = if isActive: " checked" else: ""
    let cls = if isActive:
      "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
    else:
      "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
    result &= fmt"""<label data-role="quick-exclude" data-quick-exclude-dimension="{dim}" data-quick-exclude-value="{val}" data-active="{activeStr}" class="{cls}">"""
    result &= fmt"""<input type="checkbox" name="{dim}_out" value="{val}"{checked} class="sr-only" />"""
    result &= fmt"""{capFirst(val)} <span class="rounded bg-slate-100 px-1 ml-1">{impact.getOrDefault(val, 0)}</span></label>"""
  result &= "</div>"

  # Per-dimension groups
  for dim in ["team", "status", "region"]:
    let incCounts = facetCounts(state, dim)
    let excCounts = excludeImpactCounts(state, dim)
    let dimOut    = case dim
      of "team":   state.teamOut
      of "status": state.statusOut
      else:        state.regionOut
    let dimIn     = case dim
      of "team":   state.teamIn
      of "status": state.statusIn
      else:        state.regionIn
    let options   = facetOptions.getOrDefault(dim, @[])

    result &= fmt"""<section data-filter-dimension="{dim}" class="space-y-2">"""
    result &= fmt"""<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">{capFirst(dim)}</h3>"""

    # Include sub-section
    result &= """<div data-role="include-options" class="space-y-1">"""
    result &= """<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>"""
    for option in options:
      let isExcluded  = option in dimOut
      let isChecked   = option in dimIn
      let optCount    = if isExcluded: 0 else: incCounts.getOrDefault(option, 0)
      let excludedAttr = if isExcluded: " data-excluded=\"true\"" else: ""
      let disabledAttr = if isExcluded: " disabled" else: ""
      let checkedAttr  = if isChecked:  " checked"  else: ""
      let labelExtra   = if isExcluded: " opacity-50 cursor-not-allowed" else: ""
      result &= fmt"""<label data-filter-dimension="{dim}" data-filter-option="{option}" data-filter-mode="include" data-option-count="{optCount}"{excludedAttr} class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm{labelExtra}">"""
      result &= fmt"""<span class="flex items-center gap-2"><input type="checkbox" name="{dim}_in" value="{option}"{checkedAttr}{disabledAttr} /><span class="font-medium text-slate-800">{capFirst(option)}</span></span>"""
      result &= fmt"""<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{optCount}</span></label>"""
    result &= "</div>"

    # Exclude sub-section
    result &= """<div data-role="exclude-options" class="mt-2 space-y-1">"""
    result &= """<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>"""
    for option in options:
      let isActive   = option in dimOut
      let impact     = excCounts.getOrDefault(option, 0)
      let activeAttr = if isActive: " data-active=\"true\"" else: ""
      let checkedAttr = if isActive: " checked" else: ""
      let borderCls   = if isActive: "border-red-200 bg-red-50" else: "border-slate-200"
      result &= fmt"""<label data-filter-dimension="{dim}" data-filter-option="{option}" data-filter-mode="exclude" data-option-count="{impact}"{activeAttr} class="flex items-center justify-between rounded border {borderCls} px-3 py-2 text-sm">"""
      result &= fmt"""<span class="flex items-center gap-2"><input type="checkbox" name="{dim}_out" value="{option}"{checkedAttr} /><span class="font-medium text-slate-800">{capFirst(option)}</span></span>"""
      result &= fmt"""<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{impact}</span></label>"""
    result &= "</div>"
    result &= "</section>"
  result &= "</div>"

proc renderResultsFragment(state: QueryState): string =
  let rows = filterRows(state)
  let n    = rows.len
  let fp   = fingerprint(state)
  result = fmt"""<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="{n}" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">{n} results</div>"""
  result &= fmt"""<section id="report-results" data-query-fingerprint="{fp}" data-result-count="{n}" class="space-y-2">"""
  result &= fmt"""<div data-role="active-filters" class="text-xs text-slate-500">{fp}</div>"""
  for row in rows:
    result &= fmt"""<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="{row.reportId}"><strong>{row.reportId}</strong> <span class="text-slate-500">{row.team} / {row.status} / {row.region}</span></div>"""
  result &= "</section>"

proc renderFullPage(state: QueryState): string =
  let panel = renderFilterPanel(state)
  let rows  = filterRows(state)
  let n     = rows.len
  let fp    = fingerprint(state)
  var cards = ""
  for row in rows:
    cards &= fmt"""<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="{row.reportId}"><strong>{row.reportId}</strong></div>"""
  result = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Reports</title>"
  result &= "<script src=\"https://unpkg.com/htmx.org@1.9.10\"></script>"
  result &= "<script src=\"https://cdn.tailwindcss.com\"></script></head>"
  result &= "<body class=\"p-6 font-sans\"><h1 class=\"text-xl font-bold mb-4\">Reports</h1>"
  result &= "<form id=\"report-filters\" hx-get=\"/ui/reports/results\" hx-target=\"#report-results\" hx-trigger=\"change, submit\">"
  result &= fmt"""<div class="flex gap-6"><aside class="w-64 shrink-0">{panel}</aside><main class="flex-1">"""
  result &= fmt"""<div id="result-count" data-role="result-count" data-result-count="{n}" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">{n} results</div>"""
  result &= fmt"""<section id="report-results" data-query-fingerprint="{fp}" data-result-count="{n}" class="space-y-2">{cards}</section>"""
  result &= "</main></div></form></body></html>"

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

routes:
  get "/ui/reports":
    let state = buildQueryState(request.url.query)
    resp renderFullPage(state)

  get "/ui/reports/results":
    let state = buildQueryState(request.url.query)
    resp renderResultsFragment(state)

  get "/ui/reports/filter-panel":
    let state = buildQueryState(request.url.query)
    resp renderFilterPanel(state)

  get "/healthz":
    resp """{"status":"ok"}"""
