// dart-dartfrog-faceted-filter-example.dart
//
// Demonstrates the full split include/exclude filter panel pattern with Dart Frog.
// HTML is built using StringBuffer and string interpolation.
//
// Multi-value params: context.request.uri.queryParametersAll["status_out"] ?? []
// returns List<String> with all values for repeated query params.

import 'package:dart_frog/dart_frog.dart';

// ---------------------------------------------------------------------------
// Dataset
// ---------------------------------------------------------------------------

class ReportRow {
  final String reportId;
  final String team;
  final String status;
  final String region;
  final int events;
  const ReportRow(this.reportId, this.team, this.status, this.region, this.events);
}

const reportRows = [
  ReportRow('daily-signups',     'growth',   'active',   'us',   12),
  ReportRow('trial-conversions', 'growth',   'active',   'us',   7),
  ReportRow('api-latency',       'platform', 'paused',   'eu',   5),
  ReportRow('checkout-failures', 'growth',   'active',   'eu',   9),
  ReportRow('queue-depth',       'platform', 'active',   'apac', 11),
  ReportRow('legacy-import',     'platform', 'archived', 'us',   4),
];

const facetOptions = {
  'team':   ['growth', 'platform'],
  'status': ['active', 'paused', 'archived'],
  'region': ['us', 'eu', 'apac'],
};

const quickExcludes = [
  ('status', 'archived'),
  ('status', 'paused'),
];

// ---------------------------------------------------------------------------
// Query state
// ---------------------------------------------------------------------------

class QueryState {
  final List<String> teamIn;
  final List<String> teamOut;
  final List<String> statusIn;
  final List<String> statusOut;
  final List<String> regionIn;
  final List<String> regionOut;
  final String query;
  final String sort;

  const QueryState({
    this.teamIn    = const [],
    this.teamOut   = const [],
    this.statusIn  = const [],
    this.statusOut = const [],
    this.regionIn  = const [],
    this.regionOut = const [],
    this.query     = '',
    this.sort      = 'events_desc',
  });
}

List<String> normalize(List<String>? values) {
  if (values == null || values.isEmpty) return const [];
  final seen = <String>{};
  final result = <String>[];
  for (final v in values) {
    final s = v.trim().toLowerCase();
    if (s.isNotEmpty && seen.add(s)) result.add(s);
  }
  result.sort();
  return result;
}

String normalizeSort(String s) {
  const valid = {'events_desc', 'events_asc', 'name_asc'};
  return valid.contains(s) ? s : 'events_desc';
}

QueryState buildQueryState(Uri uri) {
  final p = uri.queryParametersAll;
  final rawQuery = uri.queryParameters['query'] ?? '';
  final rawSort  = uri.queryParameters['sort']  ?? 'events_desc';
  return QueryState(
    teamIn:    normalize(p['team_in']),
    teamOut:   normalize(p['team_out']),
    statusIn:  normalize(p['status_in']),
    statusOut: normalize(p['status_out']),
    regionIn:  normalize(p['region_in']),
    regionOut: normalize(p['region_out']),
    query:     rawQuery.trim().toLowerCase(),
    sort:      normalizeSort(rawSort),
  );
}

String fingerprint(QueryState state) =>
  'team_in=${state.teamIn.join(",")}|team_out=${state.teamOut.join(",")}|'
  'status_in=${state.statusIn.join(",")}|status_out=${state.statusOut.join(",")}|'
  'region_in=${state.regionIn.join(",")}|region_out=${state.regionOut.join(",")}|'
  'query=${state.query}|sort=${state.sort}';

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

bool matchesDim(String value, List<String> includes, List<String> excludes) {
  if (includes.isNotEmpty && !includes.contains(value)) return false;
  if (excludes.isNotEmpty && excludes.contains(value)) return false;
  return true;
}

String rowDimValue(ReportRow row, String dim) => switch (dim) {
  'team'   => row.team,
  'status' => row.status,
  'region' => row.region,
  _        => '',
};

List<ReportRow> applyTextSearch(List<ReportRow> rows, String q) {
  if (q.isEmpty) return rows;
  return rows.where((row) => row.reportId.toLowerCase().contains(q)).toList();
}

List<ReportRow> sortRows(List<ReportRow> rows, String sortVal) {
  final sorted = List<ReportRow>.from(rows);
  switch (sortVal) {
    case 'events_asc':
      sorted.sort((a, b) {
        final c = a.events.compareTo(b.events);
        return c != 0 ? c : a.reportId.compareTo(b.reportId);
      });
    case 'name_asc':
      sorted.sort((a, b) => a.reportId.compareTo(b.reportId));
    default: // events_desc
      sorted.sort((a, b) {
        final c = b.events.compareTo(a.events);
        return c != 0 ? c : a.reportId.compareTo(b.reportId);
      });
  }
  return sorted;
}

List<ReportRow> filterRows(QueryState state) {
  final searched = applyTextSearch(reportRows.toList(), state.query);
  final filtered = searched.where((row) =>
    matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
    matchesDim(row.status, state.statusIn, state.statusOut) &&
    matchesDim(row.region, state.regionIn, state.regionOut)
  ).toList();
  return sortRows(filtered, state.sort);
}

Map<String, int> facetCounts(QueryState state, String dimension) {
  final options  = facetOptions[dimension] ?? [];
  final counts   = {for (final o in options) o: 0};
  final searched = applyTextSearch(reportRows.toList(), state.query);
  for (final row in searched) {
    final pass = switch (dimension) {
      'team' =>
        matchesDim(row.status, state.statusIn, state.statusOut) &&
        matchesDim(row.region, state.regionIn, state.regionOut) &&
        matchesDim(row.team,   const [],       state.teamOut),
      'status' =>
        matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
        matchesDim(row.region, state.regionIn, state.regionOut) &&
        matchesDim(row.status, const [],       state.statusOut),
      _ =>
        matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
        matchesDim(row.status, state.statusIn, state.statusOut) &&
        matchesDim(row.region, const [],       state.regionOut),
    };
    if (pass) {
      final v = rowDimValue(row, dimension);
      if (counts.containsKey(v)) counts[v] = (counts[v] ?? 0) + 1;
    }
  }
  return counts;
}

Map<String, int> excludeImpactCounts(QueryState state, String dimension) {
  final options  = facetOptions[dimension] ?? [];
  final searched = applyTextSearch(reportRows.toList(), state.query);
  final dimOut   = switch (dimension) {
    'team'   => state.teamOut,
    'status' => state.statusOut,
    _        => state.regionOut,
  };
  return {
    for (final option in options)
      option: () {
        final otherExcludes = dimOut.where((v) => v != option).toList();
        return searched.where((row) {
          final otherPass = switch (dimension) {
            'team' =>
              matchesDim(row.status, state.statusIn, state.statusOut) &&
              matchesDim(row.region, state.regionIn, state.regionOut),
            'status' =>
              matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
              matchesDim(row.region, state.regionIn, state.regionOut),
            _ =>
              matchesDim(row.team,   state.teamIn,   state.teamOut)   &&
              matchesDim(row.status, state.statusIn, state.statusOut),
          };
          final v = rowDimValue(row, dimension);
          return otherPass &&
                 (otherExcludes.isEmpty || !otherExcludes.contains(v)) &&
                 v == option;
        }).length;
      }()
  };
}

// ---------------------------------------------------------------------------
// HTML rendering
// ---------------------------------------------------------------------------

String capitalize(String s) =>
    s.isEmpty ? s : s[0].toUpperCase() + s.substring(1);

String renderFilterPanel(QueryState state) {
  final buf = StringBuffer();

  buf.write('<div id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4 space-y-4">');
  buf.write('<input type="text" name="query" value="${state.query}" placeholder="Search reports\u2026" '
      'data-role="search-input" data-search-query="${state.query}" '
      'hx-get="/ui/reports/results" hx-target="#report-results" '
      'hx-trigger="keyup changed delay:300ms" hx-include="#report-filters" />');
  buf.write('<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>');

  // Quick excludes strip
  buf.write('<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">');
  buf.write('<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>');
  for (final (dim, val) in quickExcludes) {
    final impact   = excludeImpactCounts(state, dim);
    final dimOut   = dim == 'status' ? state.statusOut : dim == 'team' ? state.teamOut : state.regionOut;
    final isActive = dimOut.contains(val);
    final activeStr = isActive ? 'true' : 'false';
    final checked   = isActive ? ' checked' : '';
    final cls = isActive
        ? 'flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer'
        : 'flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer';
    buf.write('<label data-role="quick-exclude" data-quick-exclude-dimension="$dim" data-quick-exclude-value="$val" data-active="$activeStr" class="$cls">');
    buf.write('<input type="checkbox" name="${dim}_out" value="$val"$checked class="sr-only" />');
    buf.write('${capitalize(val)} <span class="rounded bg-slate-100 px-1 ml-1">${impact[val] ?? 0}</span></label>');
  }
  buf.write('</div>');

  // Per-dimension groups
  for (final dim in ['team', 'status', 'region']) {
    final incCounts = facetCounts(state, dim);
    final excCounts = excludeImpactCounts(state, dim);
    final dimOut    = dim == 'team' ? state.teamOut : dim == 'status' ? state.statusOut : state.regionOut;
    final dimIn     = dim == 'team' ? state.teamIn  : dim == 'status' ? state.statusIn  : state.regionIn;
    final options   = facetOptions[dim] ?? [];

    buf.write('<section data-filter-dimension="$dim" class="space-y-2">');
    buf.write('<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">${capitalize(dim)}</h3>');

    // Include sub-section
    buf.write('<div data-role="include-options" class="space-y-1">');
    buf.write('<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>');
    for (final option in options) {
      final isExcluded  = dimOut.contains(option);
      final isChecked   = dimIn.contains(option);
      final optCount    = isExcluded ? 0 : (incCounts[option] ?? 0);
      final excludedAttr = isExcluded ? ' data-excluded="true"' : '';
      final disabledAttr = isExcluded ? ' disabled' : '';
      final checkedAttr  = isChecked  ? ' checked'  : '';
      final labelExtra   = isExcluded ? ' opacity-50 cursor-not-allowed' : '';
      buf.write('<label data-filter-dimension="$dim" data-filter-option="$option" data-filter-mode="include" data-option-count="$optCount"$excludedAttr class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm$labelExtra">');
      buf.write('<span class="flex items-center gap-2"><input type="checkbox" name="${dim}_in" value="$option"$checkedAttr$disabledAttr /><span class="font-medium text-slate-800">${capitalize(option)}</span></span>');
      buf.write('<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">$optCount</span></label>');
    }
    buf.write('</div>');

    // Exclude sub-section
    buf.write('<div data-role="exclude-options" class="mt-2 space-y-1">');
    buf.write('<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>');
    for (final option in options) {
      final isActive   = dimOut.contains(option);
      final impact     = excCounts[option] ?? 0;
      final activeAttr = isActive ? ' data-active="true"' : '';
      final checkedAttr = isActive ? ' checked' : '';
      final borderCls   = isActive ? 'border-red-200 bg-red-50' : 'border-slate-200';
      buf.write('<label data-filter-dimension="$dim" data-filter-option="$option" data-filter-mode="exclude" data-option-count="$impact"$activeAttr class="flex items-center justify-between rounded border $borderCls px-3 py-2 text-sm">');
      buf.write('<span class="flex items-center gap-2"><input type="checkbox" name="${dim}_out" value="$option"$checkedAttr /><span class="font-medium text-slate-800">${capitalize(option)}</span></span>');
      buf.write('<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">$impact</span></label>');
    }
    buf.write('</div>');
    buf.write('</section>');
  }
  buf.write('</div>');
  return buf.toString();
}

String renderResultsFragment(QueryState state) {
  final rows = filterRows(state);
  final n    = rows.length;
  final fp   = fingerprint(state);
  final buf  = StringBuffer();
  buf.write('<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="$n" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">$n results</div>');

  final sortEventsDescSel  = state.sort == 'events_desc' ? ' selected' : '';
  final sortEventsAscSel   = state.sort == 'events_asc'  ? ' selected' : '';
  final sortNameAscSel     = state.sort == 'name_asc'    ? ' selected' : '';
  buf.write('<select name="sort" data-role="sort-select" data-sort-order="${state.sort}" '
      'hx-get="/ui/reports/results" hx-target="#report-results" hx-include="#report-filters">');
  buf.write('<option value="events_desc"$sortEventsDescSel>Events: high \u2192 low</option>');
  buf.write('<option value="events_asc"$sortEventsAscSel>Events: low \u2192 high</option>');
  buf.write('<option value="name_asc"$sortNameAscSel>Name: A \u2192 Z</option>');
  buf.write('</select>');

  buf.write('<section id="report-results" data-query-fingerprint="$fp" data-result-count="$n" data-search-query="${state.query}" data-sort-order="${state.sort}" class="space-y-2">');
  buf.write('<div data-role="active-filters" class="text-xs text-slate-500">$fp</div>');
  for (final row in rows) {
    buf.write('<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${row.reportId}"><strong>${row.reportId}</strong> <span class="text-slate-500">${row.team} / ${row.status} / ${row.region}</span></div>');
  }
  buf.write('</section>');
  return buf.toString();
}

String renderFullPage(QueryState state) {
  final panel = renderFilterPanel(state);
  final rows  = filterRows(state);
  final n     = rows.length;
  final fp    = fingerprint(state);
  final sortEventsDescSel = state.sort == 'events_desc' ? ' selected' : '';
  final sortEventsAscSel  = state.sort == 'events_asc'  ? ' selected' : '';
  final sortNameAscSel    = state.sort == 'name_asc'    ? ' selected' : '';
  final cards = rows.map((r) => '<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="${r.reportId}"><strong>${r.reportId}</strong></div>').join('\n');
  return '''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Reports</title>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="font-sans">
<h1 class="text-xl font-bold p-4">Reports</h1>
<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">
<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">
<aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">$panel</aside>
<main id="report-results-container" class="flex-1 overflow-y-auto p-4">
<div id="result-count" data-role="result-count" data-result-count="$n" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">$n results</div>
<select name="sort" data-role="sort-select" data-sort-order="${state.sort}" hx-get="/ui/reports/results" hx-target="#report-results" hx-include="#report-filters">
<option value="events_desc"$sortEventsDescSel>Events: high \u2192 low</option>
<option value="events_asc"$sortEventsAscSel>Events: low \u2192 high</option>
<option value="name_asc"$sortNameAscSel>Name: A \u2192 Z</option>
</select>
<section id="report-results" data-query-fingerprint="$fp" data-result-count="$n" data-search-query="${state.query}" data-sort-order="${state.sort}" class="space-y-2">
$cards
</section></main></div></form></body></html>''';
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

Response onRequest(RequestContext context) {
  final uri   = context.request.uri;
  final path  = uri.path;
  final state = buildQueryState(uri);

  if (path.endsWith('/results')) {
    return Response(
      body: renderResultsFragment(state),
      headers: const {'content-type': 'text/html; charset=utf-8'},
    );
  } else if (path.endsWith('/filter-panel')) {
    return Response(
      body: renderFilterPanel(state),
      headers: const {'content-type': 'text/html; charset=utf-8'},
    );
  } else if (path == '/healthz') {
    return Response(
      body: '{"status":"ok"}',
      headers: const {'content-type': 'application/json'},
    );
  }
  return Response(
    body: renderFullPage(state),
    headers: const {'content-type': 'text/html; charset=utf-8'},
  );
}
