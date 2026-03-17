// scala-tapir-http4s-zio-faceted-filter-example.scala
//
// Demonstrates the full split include/exclude filter panel pattern with Scala + http4s + ZIO.
// HTML is built using s"""...""" multiline string interpolation.
//
// Multi-value params: req.multiParams returns Map[String, List[String]].
// Use req.multiParams.getOrElse("status_out", Nil) to collect all values.

import org.http4s.HttpRoutes
import org.http4s.MediaType
import org.http4s.dsl.Http4sDsl
import org.http4s.headers.`Content-Type`
import zio.Task

object FacetedFilterExample:
  private object Dsl extends Http4sDsl[Task]
  import Dsl.*

  // -------------------------------------------------------------------------
  // Dataset
  // -------------------------------------------------------------------------

  case class ReportRow(reportId: String, team: String, status: String, region: String, events: Int)

  val reportRows: List[ReportRow] = List(
    ReportRow("daily-signups",     "growth",   "active",   "us",   12),
    ReportRow("trial-conversions", "growth",   "active",   "us",   7),
    ReportRow("api-latency",       "platform", "paused",   "eu",   5),
    ReportRow("checkout-failures", "growth",   "active",   "eu",   9),
    ReportRow("queue-depth",       "platform", "active",   "apac", 11),
    ReportRow("legacy-import",     "platform", "archived", "us",   4),
  )

  val facetOptions: Map[String, List[String]] = Map(
    "team"   -> List("growth", "platform"),
    "status" -> List("active", "paused", "archived"),
    "region" -> List("us", "eu", "apac"),
  )

  val quickExcludes: List[(String, String)] = List(
    "status" -> "archived",
    "status" -> "paused",
  )

  // -------------------------------------------------------------------------
  // Query state
  // -------------------------------------------------------------------------

  case class QueryState(
    teamIn:    List[String] = Nil,
    teamOut:   List[String] = Nil,
    statusIn:  List[String] = Nil,
    statusOut: List[String] = Nil,
    regionIn:  List[String] = Nil,
    regionOut: List[String] = Nil,
    query:     String = "",
    sort:      String = "events_desc",
  )

  def normalize(values: List[String]): List[String] =
    values.map(_.trim.toLowerCase).filter(_.nonEmpty).sorted.distinct

  def normalizeSort(s: String): String =
    if Set("events_desc", "events_asc", "name_asc").contains(s) then s else "events_desc"

  def buildQueryState(params: Map[String, List[String]]): QueryState = QueryState(
    teamIn    = normalize(params.getOrElse("team_in",    Nil)),
    teamOut   = normalize(params.getOrElse("team_out",   Nil)),
    statusIn  = normalize(params.getOrElse("status_in",  Nil)),
    statusOut = normalize(params.getOrElse("status_out", Nil)),
    regionIn  = normalize(params.getOrElse("region_in",  Nil)),
    regionOut = normalize(params.getOrElse("region_out", Nil)),
    query     = params.getOrElse("query", Nil).headOption.getOrElse("").trim.toLowerCase,
    sort      = normalizeSort(params.getOrElse("sort", Nil).headOption.getOrElse("")),
  )

  def fingerprint(state: QueryState): String =
    s"team_in=${state.teamIn.mkString(",")}|team_out=${state.teamOut.mkString(",")}|" +
    s"status_in=${state.statusIn.mkString(",")}|status_out=${state.statusOut.mkString(",")}|" +
    s"region_in=${state.regionIn.mkString(",")}|region_out=${state.regionOut.mkString(",")}|" +
    s"query=${state.query}|sort=${state.sort}"

  // -------------------------------------------------------------------------
  // Filter helpers
  // -------------------------------------------------------------------------

  def matchesDim(value: String, includes: List[String], excludes: List[String]): Boolean =
    (includes.isEmpty || includes.contains(value)) &&
    (excludes.isEmpty || !excludes.contains(value))

  def rowDimValue(row: ReportRow, dim: String): String = dim match
    case "team"   => row.team
    case "status" => row.status
    case "region" => row.region
    case _        => ""

  def applyTextSearch(rows: List[ReportRow], q: String): List[ReportRow] =
    if q.isEmpty then rows
    else rows.filter(_.reportId.toLowerCase.contains(q))

  def sortRows(rows: List[ReportRow], sortVal: String): List[ReportRow] = sortVal match
    case "events_asc" => rows.sortWith((a, b) => a.events < b.events || (a.events == b.events && a.reportId < b.reportId))
    case "name_asc"   => rows.sortBy(_.reportId)
    case _            => rows.sortWith((a, b) => a.events > b.events || (a.events == b.events && a.reportId < b.reportId))

  def filterRows(state: QueryState): List[ReportRow] =
    val searched = applyTextSearch(reportRows, state.query)
    val filtered = searched.filter { row =>
      matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
      matchesDim(row.status, state.statusIn, state.statusOut) &&
      matchesDim(row.region, state.regionIn, state.regionOut)
    }
    sortRows(filtered, state.sort)

  def facetCounts(state: QueryState, dimension: String): Map[String, Int] =
    val options  = facetOptions.getOrElse(dimension, Nil)
    val init     = options.map(_ -> 0).toMap
    val searched = applyTextSearch(reportRows, state.query)
    val filtered = dimension match
      case "team" =>
        searched.filter(r =>
          matchesDim(r.status, state.statusIn, state.statusOut) &&
          matchesDim(r.region, state.regionIn, state.regionOut) &&
          matchesDim(r.team,   Nil,            state.teamOut))
      case "status" =>
        searched.filter(r =>
          matchesDim(r.team,   state.teamIn,   state.teamOut)   &&
          matchesDim(r.region, state.regionIn, state.regionOut) &&
          matchesDim(r.status, Nil,            state.statusOut))
      case _ =>
        searched.filter(r =>
          matchesDim(r.team,   state.teamIn,   state.teamOut)   &&
          matchesDim(r.status, state.statusIn, state.statusOut) &&
          matchesDim(r.region, Nil,            state.regionOut))
    filtered.foldLeft(init) { (acc, row) =>
      val v = rowDimValue(row, dimension)
      if acc.contains(v) then acc.updated(v, acc(v) + 1) else acc
    }

  def excludeImpactCounts(state: QueryState, dimension: String): Map[String, Int] =
    val options  = facetOptions.getOrElse(dimension, Nil)
    val dimOut   = dimension match
      case "team"   => state.teamOut
      case "status" => state.statusOut
      case _        => state.regionOut
    val searched = applyTextSearch(reportRows, state.query)
    options.map { option =>
      val otherExcludes = dimOut.filterNot(_ == option)
      val count = searched.count { row =>
        val otherPass = dimension match
          case "team" =>
            matchesDim(row.status, state.statusIn, state.statusOut) &&
            matchesDim(row.region, state.regionIn, state.regionOut)
          case "status" =>
            matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
            matchesDim(row.region, state.regionIn, state.regionOut)
          case _ =>
            matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
            matchesDim(row.status, state.statusIn, state.statusOut)
        val v = rowDimValue(row, dimension)
        otherPass && (otherExcludes.isEmpty || !otherExcludes.contains(v)) && v == option
      }
      option -> count
    }.toMap

  // -------------------------------------------------------------------------
  // HTML rendering
  // -------------------------------------------------------------------------

  def capitalize(s: String): String = if s.isEmpty then s else s.head.toUpper +: s.tail

  def sortSelectHtml(state: QueryState): String =
    def sel(v: String) = if state.sort == v then " selected" else ""
    s"""<select name="sort" data-role="sort-select" data-sort-order="${state.sort}" hx-get="/ui/reports/results" hx-target="#report-results" hx-include="#report-filters">""" +
    s"""<option value="events_desc"${sel("events_desc")}>Events: high &rarr; low</option>""" +
    s"""<option value="events_asc"${sel("events_asc")}>Events: low &rarr; high</option>""" +
    s"""<option value="name_asc"${sel("name_asc")}>Name: A &rarr; Z</option>""" +
    "</select>"

  def renderQuickExcludes(state: QueryState): String =
    val buttons = quickExcludes.map { (dim, v) =>
      val impact   = excludeImpactCounts(state, dim)
      val dimOut   = if dim == "team" then state.teamOut else if dim == "status" then state.statusOut else state.regionOut
      val isActive = dimOut.contains(v)
      val activeStr = if isActive then "true" else "false"
      val checked   = if isActive then " checked" else ""
      val cls = if isActive
        then "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
        else "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
      s"""<label data-role="quick-exclude" data-quick-exclude-dimension="$dim" data-quick-exclude-value="$v" data-active="$activeStr" class="$cls">""" +
      s"""<input type="checkbox" name="${dim}_out" value="$v"$checked class="sr-only" />""" +
      s"""${capitalize(v)} <span class="rounded bg-slate-100 px-1 ml-1">${impact.getOrElse(v, 0)}</span></label>"""
    }.mkString
    s"""<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">""" +
    s"""<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>$buttons</div>"""

  def renderDimensionGroup(state: QueryState, dim: String): String =
    val incCounts = facetCounts(state, dim)
    val excCounts = excludeImpactCounts(state, dim)
    val dimOut    = if dim == "team" then state.teamOut else if dim == "status" then state.statusOut else state.regionOut
    val dimIn     = if dim == "team" then state.teamIn  else if dim == "status" then state.statusIn  else state.regionIn
    val options   = facetOptions.getOrElse(dim, Nil)

    val incOpts = options.map { option =>
      val isExcluded  = dimOut.contains(option)
      val isChecked   = dimIn.contains(option)
      val optCount    = if isExcluded then 0 else incCounts.getOrElse(option, 0)
      val excludedAttr = if isExcluded then """ data-excluded="true"""" else ""
      val disabledAttr = if isExcluded then " disabled" else ""
      val checkedAttr  = if isChecked  then " checked"  else ""
      val labelExtra   = if isExcluded then " opacity-50 cursor-not-allowed" else ""
      s"""<label data-filter-dimension="$dim" data-filter-option="$option" data-filter-mode="include" data-option-count="$optCount"$excludedAttr class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm$labelExtra">""" +
      s"""<span class="flex items-center gap-2"><input type="checkbox" name="${dim}_in" value="$option"$checkedAttr$disabledAttr /><span class="font-medium text-slate-800">${capitalize(option)}</span></span>""" +
      s"""<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">$optCount</span></label>"""
    }.mkString

    val excOpts = options.map { option =>
      val isActive  = dimOut.contains(option)
      val impact    = excCounts.getOrElse(option, 0)
      val activeAttr = if isActive then """ data-active="true"""" else ""
      val checkedAttr = if isActive then " checked" else ""
      val borderCls   = if isActive then "border-red-200 bg-red-50" else "border-slate-200"
      s"""<label data-filter-dimension="$dim" data-filter-option="$option" data-filter-mode="exclude" data-option-count="$impact"$activeAttr class="flex items-center justify-between rounded border $borderCls px-3 py-2 text-sm">""" +
      s"""<span class="flex items-center gap-2"><input type="checkbox" name="${dim}_out" value="$option"$checkedAttr /><span class="font-medium text-slate-800">${capitalize(option)}</span></span>""" +
      s"""<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">$impact</span></label>"""
    }.mkString

    s"""<section data-filter-dimension="$dim" class="space-y-2">""" +
    s"""<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">${capitalize(dim)}</h3>""" +
    s"""<div data-role="include-options" class="space-y-1"><p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>$incOpts</div>""" +
    s"""<div data-role="exclude-options" class="mt-2 space-y-1"><p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>$excOpts</div>""" +
    "</section>"

  def renderFilterPanel(state: QueryState): String =
    val qEsc      = state.query.replace("\"", "&quot;")
    val searchInput =
      s"""<input type="text" name="query" value="$qEsc" placeholder="Search reports&hellip;" """ +
      s"""data-role="search-input" data-search-query="$qEsc" """ +
      s"""hx-get="/ui/reports/results" hx-target="#report-results" """ +
      s"""hx-trigger="keyup changed delay:300ms" hx-include="#report-filters" """ +
      s"""class="w-full rounded border border-slate-300 px-3 py-2 text-sm" />"""
    val quickStrip = renderQuickExcludes(state)
    val dimGroups  = List("team", "status", "region").map(renderDimensionGroup(state, _)).mkString
    s"""<div id="filter-panel" class="space-y-4">""" +
    s"""<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>""" +
    searchInput + quickStrip + dimGroups + "</div>"

  def renderResultsFragment(state: QueryState): String =
    val rows  = filterRows(state)
    val n     = rows.size
    val fp    = fingerprint(state)
    val cards = rows.map(r =>
      s"""<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${r.reportId}"><strong>${r.reportId}</strong> <span class="text-slate-500">${r.team} / ${r.status} / ${r.region}</span></div>"""
    ).mkString("\n")
    s"""<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="$n" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">$n results</div>""" +
    sortSelectHtml(state) +
    s"""<section id="report-results" data-query-fingerprint="$fp" data-result-count="$n" data-search-query="${state.query}" data-sort-order="${state.sort}" class="space-y-2">""" +
    s"""<div data-role="active-filters" class="text-xs text-slate-500">$fp</div>$cards</section>"""

  def renderFullPage(state: QueryState): String =
    val panel = renderFilterPanel(state)
    val rows  = filterRows(state)
    val n     = rows.size
    val fp    = fingerprint(state)
    val cards = rows.map(r =>
      s"""<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${r.reportId}"><strong>${r.reportId}</strong></div>"""
    ).mkString("\n")
    s"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Reports</title>""" +
    s"""<script src="https://unpkg.com/htmx.org@1.9.10"></script><script src="https://cdn.tailwindcss.com"></script></head>""" +
    s"""<body class="font-sans"><h1 class="text-xl font-bold p-4">Reports</h1>""" +
    s"""<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">""" +
    s"""<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">""" +
    s"""<aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">$panel</aside>""" +
    s"""<main id="report-results-container" class="flex-1 overflow-y-auto p-4">""" +
    s"""<div id="result-count" data-role="result-count" data-result-count="$n" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">$n results</div>""" +
    sortSelectHtml(state) +
    s"""<section id="report-results" data-query-fingerprint="$fp" data-result-count="$n" data-search-query="${state.query}" data-sort-order="${state.sort}" class="space-y-2">$cards</section>""" +
    "</main></div></form></body></html>"

  // -------------------------------------------------------------------------
  // Routes
  // -------------------------------------------------------------------------

  val routes: HttpRoutes[Task] =
    HttpRoutes.of[Task] {
      case req @ GET -> Root / "ui" / "reports" =>
        val state = buildQueryState(req.multiParams)
        Ok(renderFullPage(state)).map(_.withContentType(`Content-Type`(MediaType.text.html)))

      case req @ GET -> Root / "ui" / "reports" / "results" =>
        val state = buildQueryState(req.multiParams)
        Ok(renderResultsFragment(state)).map(_.withContentType(`Content-Type`(MediaType.text.html)))

      case req @ GET -> Root / "ui" / "reports" / "filter-panel" =>
        val state = buildQueryState(req.multiParams)
        Ok(renderFilterPanel(state)).map(_.withContentType(`Content-Type`(MediaType.text.html)))

      case GET -> Root / "healthz" =>
        Ok("""{"status":"ok"}""")
    }
