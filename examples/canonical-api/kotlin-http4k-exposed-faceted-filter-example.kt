// kotlin-http4k-exposed-faceted-filter-example.kt
//
// Demonstrates the full split include/exclude filter panel pattern with Kotlin + http4k.
// HTML is built with buildString { append(...) }. A real app would use a template engine.
//
// Multi-value params: request.queries("status_out") returns List<String?>.
// Use .filterNotNull() to collect all values.

import org.http4k.core.Method.GET
import org.http4k.core.Request
import org.http4k.core.Response
import org.http4k.core.Status.Companion.OK
import org.http4k.routing.bind
import org.http4k.routing.routes

// ---------------------------------------------------------------------------
// Dataset
// ---------------------------------------------------------------------------

data class ReportRow(
    val reportId: String,
    val team:     String,
    val status:   String,
    val region:   String,
    val events:   Int,
)

val REPORT_ROWS = listOf(
    ReportRow("daily-signups",     "growth",   "active",   "us",   12),
    ReportRow("trial-conversions", "growth",   "active",   "us",   7),
    ReportRow("api-latency",       "platform", "paused",   "eu",   5),
    ReportRow("checkout-failures", "growth",   "active",   "eu",   9),
    ReportRow("queue-depth",       "platform", "active",   "apac", 11),
    ReportRow("legacy-import",     "platform", "archived", "us",   4),
)

val FACET_OPTIONS: Map<String, List<String>> = mapOf(
    "team"   to listOf("growth", "platform"),
    "status" to listOf("active", "paused", "archived"),
    "region" to listOf("us", "eu", "apac"),
)

val QUICK_EXCLUDES: List<Pair<String, String>> = listOf(
    "status" to "archived",
    "status" to "paused",
)

// ---------------------------------------------------------------------------
// Query state
// ---------------------------------------------------------------------------

data class QueryState(
    val teamIn:    List<String> = emptyList(),
    val teamOut:   List<String> = emptyList(),
    val statusIn:  List<String> = emptyList(),
    val statusOut: List<String> = emptyList(),
    val regionIn:  List<String> = emptyList(),
    val regionOut: List<String> = emptyList(),
)

fun normalize(values: List<String?>): List<String> =
    values.filterNotNull()
        .map { it.trim().lowercase() }
        .filter { it.isNotEmpty() }
        .toSortedSet()
        .toList()

fun buildQueryState(request: Request): QueryState = QueryState(
    teamIn    = normalize(request.queries("team_in")),
    teamOut   = normalize(request.queries("team_out")),
    statusIn  = normalize(request.queries("status_in")),
    statusOut = normalize(request.queries("status_out")),
    regionIn  = normalize(request.queries("region_in")),
    regionOut = normalize(request.queries("region_out")),
)

fun fingerprint(state: QueryState): String = buildString {
    append("team_in=${state.teamIn.joinToString(",")}")
    append("|team_out=${state.teamOut.joinToString(",")}")
    append("|status_in=${state.statusIn.joinToString(",")}")
    append("|status_out=${state.statusOut.joinToString(",")}")
    append("|region_in=${state.regionIn.joinToString(",")}")
    append("|region_out=${state.regionOut.joinToString(",")}")
}

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

fun matchesDim(value: String, includes: List<String>, excludes: List<String>): Boolean =
    (includes.isEmpty() || includes.contains(value)) &&
    (excludes.isEmpty() || !excludes.contains(value))

fun rowDimValue(row: ReportRow, dim: String): String = when (dim) {
    "team"   -> row.team
    "status" -> row.status
    "region" -> row.region
    else     -> ""
}

fun filterRows(state: QueryState): List<ReportRow> =
    REPORT_ROWS.filter { row ->
        matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
        matchesDim(row.status, state.statusIn, state.statusOut) &&
        matchesDim(row.region, state.regionIn, state.regionOut)
    }

fun facetCounts(state: QueryState, dimension: String): Map<String, Int> {
    val options = FACET_OPTIONS[dimension] ?: emptyList()
    val counts  = options.associateWith { 0 }.toMutableMap()

    for (row in REPORT_ROWS) {
        val pass = when (dimension) {
            "team" ->
                matchesDim(row.status, state.statusIn, state.statusOut) &&
                matchesDim(row.region, state.regionIn, state.regionOut) &&
                matchesDim(row.team,   emptyList(),    state.teamOut)
            "status" ->
                matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
                matchesDim(row.region, state.regionIn, state.regionOut) &&
                matchesDim(row.status, emptyList(),    state.statusOut)
            else ->
                matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
                matchesDim(row.status, state.statusIn, state.statusOut) &&
                matchesDim(row.region, emptyList(),    state.regionOut)
        }
        if (pass) {
            val v = rowDimValue(row, dimension)
            if (v in counts) counts[v] = (counts[v] ?: 0) + 1
        }
    }
    return counts
}

fun excludeImpactCounts(state: QueryState, dimension: String): Map<String, Int> {
    val options = FACET_OPTIONS[dimension] ?: emptyList()
    val dimOut  = when (dimension) {
        "team"   -> state.teamOut
        "status" -> state.statusOut
        else     -> state.regionOut
    }
    return options.associateWith { option ->
        val otherExcludes = dimOut.filter { it != option }
        REPORT_ROWS.count { row ->
            val otherPass = when (dimension) {
                "team" ->
                    matchesDim(row.status, state.statusIn, state.statusOut) &&
                    matchesDim(row.region, state.regionIn, state.regionOut)
                "status" ->
                    matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
                    matchesDim(row.region, state.regionIn, state.regionOut)
                else ->
                    matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
                    matchesDim(row.status, state.statusIn, state.statusOut)
            }
            val v = rowDimValue(row, dimension)
            otherPass &&
            (otherExcludes.isEmpty() || !otherExcludes.contains(v)) &&
            v == option
        }
    }
}

// ---------------------------------------------------------------------------
// HTML rendering
// ---------------------------------------------------------------------------

fun renderFilterPanel(state: QueryState): String = buildString {
    append("""<div id="filter-panel" class="space-y-4">""")
    append("""<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>""")

    // Quick excludes strip
    append("""<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">""")
    append("""<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>""")
    for ((dim, val) in QUICK_EXCLUDES) {
        val impact   = excludeImpactCounts(state, dim)
        val dimOut   = when (dim) { "status" -> state.statusOut; "team" -> state.teamOut; else -> state.regionOut }
        val isActive = dimOut.contains(val)
        val activeStr = if (isActive) "true" else "false"
        val checked   = if (isActive) " checked" else ""
        val cls = if (isActive)
            "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
        else
            "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
        append("""<label data-role="quick-exclude" data-quick-exclude-dimension="$dim" data-quick-exclude-value="$val" data-active="$activeStr" class="$cls">""")
        append("""<input type="checkbox" name="${dim}_out" value="$val"$checked class="sr-only" />""")
        append("""${val.replaceFirstChar { it.uppercase() }} <span class="rounded bg-slate-100 px-1 ml-1">${impact[val] ?: 0}</span></label>""")
    }
    append("</div>")

    // Per-dimension groups
    for (dim in listOf("team", "status", "region")) {
        val incCounts = facetCounts(state, dim)
        val excCounts = excludeImpactCounts(state, dim)
        val dimOut    = when (dim) { "team" -> state.teamOut; "status" -> state.statusOut; else -> state.regionOut }
        val dimIn     = when (dim) { "team" -> state.teamIn;  "status" -> state.statusIn;  else -> state.regionIn  }
        val options   = FACET_OPTIONS[dim] ?: emptyList()

        append("""<section data-filter-dimension="$dim" class="space-y-2">""")
        append("""<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">${dim.replaceFirstChar { it.uppercase() }}</h3>""")

        // Include sub-section
        append("""<div data-role="include-options" class="space-y-1">""")
        append("""<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>""")
        for (option in options) {
            val isExcluded   = dimOut.contains(option)
            val isChecked    = dimIn.contains(option)
            val optCount     = if (isExcluded) 0 else (incCounts[option] ?: 0)
            val excludedAttr = if (isExcluded) """ data-excluded="true"""" else ""
            val disabledAttr = if (isExcluded) " disabled" else ""
            val checkedAttr  = if (isChecked)  " checked"  else ""
            val labelExtra   = if (isExcluded) " opacity-50 cursor-not-allowed" else ""
            append("""<label data-filter-dimension="$dim" data-filter-option="$option" data-filter-mode="include" data-option-count="$optCount"$excludedAttr class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm$labelExtra">""")
            append("""<span class="flex items-center gap-2"><input type="checkbox" name="${dim}_in" value="$option"$checkedAttr$disabledAttr /><span class="font-medium text-slate-800">${option.replaceFirstChar { it.uppercase() }}</span></span>""")
            append("""<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">$optCount</span></label>""")
        }
        append("</div>")

        // Exclude sub-section
        append("""<div data-role="exclude-options" class="mt-2 space-y-1">""")
        append("""<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>""")
        for (option in options) {
            val isActive   = dimOut.contains(option)
            val impact     = excCounts[option] ?: 0
            val activeAttr = if (isActive) """ data-active="true"""" else ""
            val checkedAttr = if (isActive) " checked" else ""
            val borderCls   = if (isActive) "border-red-200 bg-red-50" else "border-slate-200"
            append("""<label data-filter-dimension="$dim" data-filter-option="$option" data-filter-mode="exclude" data-option-count="$impact"$activeAttr class="flex items-center justify-between rounded border $borderCls px-3 py-2 text-sm">""")
            append("""<span class="flex items-center gap-2"><input type="checkbox" name="${dim}_out" value="$option"$checkedAttr /><span class="font-medium text-slate-800">${option.replaceFirstChar { it.uppercase() }}</span></span>""")
            append("""<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">$impact</span></label>""")
        }
        append("</div>")
        append("</section>")
    }
    append("</div>")
}

fun renderResultsFragment(state: QueryState): String {
    val rows = filterRows(state)
    val n    = rows.size
    val fp   = fingerprint(state)
    return buildString {
        append("""<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="$n" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">$n results</div>""")
        append("""<section id="report-results" data-query-fingerprint="$fp" data-result-count="$n" class="space-y-2">""")
        append("""<div data-role="active-filters" class="text-xs text-slate-500">$fp</div>""")
        for (row in rows) {
            append("""<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${row.reportId}"><strong>${row.reportId}</strong> <span class="text-slate-500">${row.team} / ${row.status} / ${row.region}</span></div>""")
        }
        append("</section>")
    }
}

fun renderFullPage(state: QueryState): String {
    val panel = renderFilterPanel(state)
    val rows  = filterRows(state)
    val n     = rows.size
    val fp    = fingerprint(state)
    return buildString {
        append("""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Reports</title>""")
        append("""<script src="https://unpkg.com/htmx.org@1.9.10"></script>""")
        append("""<script src="https://cdn.tailwindcss.com"></script></head>""")
        append("""<body class="p-6 font-sans"><h1 class="text-xl font-bold mb-4">Reports</h1>""")
        append("""<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">""")
        append("""<div class="flex gap-6"><aside class="w-64 shrink-0">$panel</aside><main class="flex-1">""")
        append("""<div id="result-count" data-role="result-count" data-result-count="$n" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">$n results</div>""")
        append("""<section id="report-results" data-query-fingerprint="$fp" data-result-count="$n" class="space-y-2">""")
        for (row in rows) {
            append("""<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${row.reportId}"><strong>${row.reportId}</strong></div>""")
        }
        append("</section></main></div></form></body></html>")
    }
}

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

val appRoutes = routes(
    "/ui/reports" bind GET to { request ->
        Response(OK).header("content-type", "text/html; charset=utf-8")
            .body(renderFullPage(buildQueryState(request)))
    },
    "/ui/reports/results" bind GET to { request ->
        Response(OK).header("content-type", "text/html; charset=utf-8")
            .body(renderResultsFragment(buildQueryState(request)))
    },
    "/ui/reports/filter-panel" bind GET to { request ->
        Response(OK).header("content-type", "text/html; charset=utf-8")
            .body(renderFilterPanel(buildQueryState(request)))
    },
    "/healthz" bind GET to {
        Response(OK).header("content-type", "application/json").body("""{"status":"ok"}""")
    },
)
