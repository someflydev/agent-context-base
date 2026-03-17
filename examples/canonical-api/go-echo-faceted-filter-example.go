// go-echo-faceted-filter-example.go
//
// Demonstrates the full split include/exclude filter panel pattern with Go + Echo.
// HTML is built using strings.Builder. See go-echo-faceted-filter-panel-template.templ
// for the typed templ equivalent.
//
// Multi-value params: c.QueryParams()["status_out"] returns []string.

package main

import (
	"fmt"
	"net/http"
	"sort"
	"strings"

	"github.com/labstack/echo/v4"
)

// ---------------------------------------------------------------------------
// Dataset
// ---------------------------------------------------------------------------

type ReportRow struct {
	ReportID string
	Team     string
	Status   string
	Region   string
	Events   int
}

var reportRows = []ReportRow{
	{"daily-signups", "growth", "active", "us", 12},
	{"trial-conversions", "growth", "active", "us", 7},
	{"api-latency", "platform", "paused", "eu", 5},
	{"checkout-failures", "growth", "active", "eu", 9},
	{"queue-depth", "platform", "active", "apac", 11},
	{"legacy-import", "platform", "archived", "us", 4},
}

var facetOptions = map[string][]string{
	"team":   {"growth", "platform"},
	"status": {"active", "paused", "archived"},
	"region": {"us", "eu", "apac"},
}

var quickExcludes = [][2]string{
	{"status", "archived"},
	{"status", "paused"},
}

// ---------------------------------------------------------------------------
// Query state
// ---------------------------------------------------------------------------

type QueryState struct {
	TeamIn    []string
	TeamOut   []string
	StatusIn  []string
	StatusOut []string
	RegionIn  []string
	RegionOut []string
	Query     string
	Sort      string
}

func normalize(values []string) []string {
	seen := map[string]bool{}
	result := []string{}
	for _, v := range values {
		s := strings.ToLower(strings.TrimSpace(v))
		if s != "" && !seen[s] {
			seen[s] = true
			result = append(result, s)
		}
	}
	sort.Strings(result)
	return result
}

func normalizeSort(s string) string {
	switch s {
	case "events_desc", "events_asc", "name_asc":
		return s
	}
	return "events_desc"
}

func buildQueryState(c echo.Context) QueryState {
	q := c.QueryParams()
	return QueryState{
		TeamIn:    normalize(q["team_in"]),
		TeamOut:   normalize(q["team_out"]),
		StatusIn:  normalize(q["status_in"]),
		StatusOut: normalize(q["status_out"]),
		RegionIn:  normalize(q["region_in"]),
		RegionOut: normalize(q["region_out"]),
		Query:     strings.TrimSpace(strings.ToLower(c.QueryParam("query"))),
		Sort:      normalizeSort(c.QueryParam("sort")),
	}
}

func fingerprint(s QueryState) string {
	return fmt.Sprintf(
		"team_in=%s|team_out=%s|status_in=%s|status_out=%s|region_in=%s|region_out=%s|query=%s|sort=%s",
		strings.Join(s.TeamIn, ","),
		strings.Join(s.TeamOut, ","),
		strings.Join(s.StatusIn, ","),
		strings.Join(s.StatusOut, ","),
		strings.Join(s.RegionIn, ","),
		strings.Join(s.RegionOut, ","),
		s.Query,
		s.Sort,
	)
}

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

func contains(slice []string, s string) bool {
	for _, v := range slice {
		if v == s {
			return true
		}
	}
	return false
}

func matchesDim(value string, includes, excludes []string) bool {
	if len(includes) > 0 && !contains(includes, value) {
		return false
	}
	if len(excludes) > 0 && contains(excludes, value) {
		return false
	}
	return true
}

func applyTextSearch(rows []ReportRow, q string) []ReportRow {
	if q == "" {
		return rows
	}
	var result []ReportRow
	for _, row := range rows {
		if strings.Contains(strings.ToLower(row.ReportID), q) {
			result = append(result, row)
		}
	}
	return result
}

func sortRows(rows []ReportRow, sortVal string) []ReportRow {
	cp := make([]ReportRow, len(rows))
	copy(cp, rows)
	switch sortVal {
	case "events_asc":
		sort.Slice(cp, func(i, j int) bool {
			if cp[i].Events != cp[j].Events {
				return cp[i].Events < cp[j].Events
			}
			return cp[i].ReportID < cp[j].ReportID
		})
	case "name_asc":
		sort.Slice(cp, func(i, j int) bool {
			return cp[i].ReportID < cp[j].ReportID
		})
	default: // events_desc
		sort.Slice(cp, func(i, j int) bool {
			if cp[i].Events != cp[j].Events {
				return cp[i].Events > cp[j].Events
			}
			return cp[i].ReportID < cp[j].ReportID
		})
	}
	return cp
}

func filterRows(state QueryState) []ReportRow {
	base := applyTextSearch(reportRows, state.Query)
	var result []ReportRow
	for _, row := range base {
		if matchesDim(row.Team, state.TeamIn, state.TeamOut) &&
			matchesDim(row.Status, state.StatusIn, state.StatusOut) &&
			matchesDim(row.Region, state.RegionIn, state.RegionOut) {
			result = append(result, row)
		}
	}
	return result
}

func rowDimValue(row ReportRow, dim string) string {
	switch dim {
	case "team":
		return row.Team
	case "status":
		return row.Status
	case "region":
		return row.Region
	}
	return ""
}

func facetCounts(state QueryState, dimension string) map[string]int {
	options := facetOptions[dimension]
	counts := map[string]int{}
	for _, o := range options {
		counts[o] = 0
	}
	base := applyTextSearch(reportRows, state.Query)
	for _, row := range base {
		var pass bool
		switch dimension {
		case "team":
			pass = matchesDim(row.Status, state.StatusIn, state.StatusOut) &&
				matchesDim(row.Region, state.RegionIn, state.RegionOut) &&
				matchesDim(row.Team, nil, state.TeamOut)
		case "status":
			pass = matchesDim(row.Team, state.TeamIn, state.TeamOut) &&
				matchesDim(row.Region, state.RegionIn, state.RegionOut) &&
				matchesDim(row.Status, nil, state.StatusOut)
		case "region":
			pass = matchesDim(row.Team, state.TeamIn, state.TeamOut) &&
				matchesDim(row.Status, state.StatusIn, state.StatusOut) &&
				matchesDim(row.Region, nil, state.RegionOut)
		}
		if pass {
			val := rowDimValue(row, dimension)
			if _, ok := counts[val]; ok {
				counts[val]++
			}
		}
	}
	return counts
}

func excludeImpactCounts(state QueryState, dimension string) map[string]int {
	options := facetOptions[dimension]
	counts := map[string]int{}
	var dimOut []string
	switch dimension {
	case "team":
		dimOut = state.TeamOut
	case "status":
		dimOut = state.StatusOut
	case "region":
		dimOut = state.RegionOut
	}

	base := applyTextSearch(reportRows, state.Query)
	for _, option := range options {
		otherExcludes := []string{}
		for _, v := range dimOut {
			if v != option {
				otherExcludes = append(otherExcludes, v)
			}
		}
		count := 0
		for _, row := range base {
			var otherPass bool
			switch dimension {
			case "team":
				otherPass = matchesDim(row.Status, state.StatusIn, state.StatusOut) &&
					matchesDim(row.Region, state.RegionIn, state.RegionOut)
			case "status":
				otherPass = matchesDim(row.Team, state.TeamIn, state.TeamOut) &&
					matchesDim(row.Region, state.RegionIn, state.RegionOut)
			case "region":
				otherPass = matchesDim(row.Team, state.TeamIn, state.TeamOut) &&
					matchesDim(row.Status, state.StatusIn, state.StatusOut)
			}
			val := rowDimValue(row, dimension)
			if otherPass &&
				(len(otherExcludes) == 0 || !contains(otherExcludes, val)) &&
				val == option {
				count++
			}
		}
		counts[option] = count
	}
	return counts
}

// capitalize returns s with the first letter uppercased (avoids deprecated strings.Title).
func capitalize(s string) string {
	if s == "" {
		return s
	}
	return strings.ToUpper(s[:1]) + s[1:]
}

// ---------------------------------------------------------------------------
// HTML rendering
// ---------------------------------------------------------------------------

func renderFilterPanel(state QueryState) string {
	var b strings.Builder

	b.WriteString(`<div id="filter-panel" class="space-y-4">`)
	b.WriteString(`<div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">Counts reflect the active backend query semantics.</div>`)

	// Search input (above quick excludes strip)
	fmt.Fprintf(&b,
		`<input type="text" name="query" value=%q placeholder="Search reports&#x2026;"` +
			` data-role="search-input" data-search-query=%q` +
			` hx-get="/ui/reports/results" hx-target="#report-results"` +
			` hx-trigger="keyup changed delay:300ms" hx-include="#report-filters"` +
			` class="w-full rounded border border-slate-300 px-3 py-2 text-sm" />`,
		state.Query, state.Query,
	)

	// Quick excludes strip
	b.WriteString(`<div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3" data-role="quick-excludes-strip">`)
	b.WriteString(`<span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>`)
	for _, qe := range quickExcludes {
		dim, val := qe[0], qe[1]
		impact := excludeImpactCounts(state, dim)
		var dimOut []string
		switch dim {
		case "status":
			dimOut = state.StatusOut
		}
		isActive := contains(dimOut, val)
		activeStr := "false"
		checked := ""
		cls := "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
		if isActive {
			activeStr = "true"
			checked = " checked"
			cls = "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
		}
		fmt.Fprintf(&b,
			`<label data-role="quick-exclude" data-quick-exclude-dimension=%q data-quick-exclude-value=%q data-active=%q class=%q>`+
				`<input type="checkbox" name="%s_out" value=%q%s class="sr-only" />`+
				`%s <span class="rounded bg-slate-100 px-1 ml-1">%d</span></label>`,
			dim, val, activeStr, cls, dim, val, checked, capitalize(val), impact[val],
		)
	}
	b.WriteString(`</div>`)

	// Per-dimension groups
	for _, dim := range []string{"team", "status", "region"} {
		incCounts := facetCounts(state, dim)
		excCounts := excludeImpactCounts(state, dim)
		options := facetOptions[dim]
		var dimOut, dimIn []string
		switch dim {
		case "team":
			dimOut = state.TeamOut
			dimIn = state.TeamIn
		case "status":
			dimOut = state.StatusOut
			dimIn = state.StatusIn
		case "region":
			dimOut = state.RegionOut
			dimIn = state.RegionIn
		}

		fmt.Fprintf(&b, `<section data-filter-dimension=%q class="space-y-2">`, dim)
		fmt.Fprintf(&b, `<h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">%s</h3>`, capitalize(dim))

		// Include sub-section
		b.WriteString(`<div data-role="include-options" class="space-y-1">`)
		b.WriteString(`<p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>`)
		for _, option := range options {
			isExcluded := contains(dimOut, option)
			isChecked := contains(dimIn, option)
			optCount := incCounts[option]
			if isExcluded {
				optCount = 0
			}
			excludedAttr := ""
			disabledAttr := ""
			checkedAttr := ""
			labelExtra := ""
			if isExcluded {
				excludedAttr = ` data-excluded="true"`
				disabledAttr = " disabled"
				labelExtra = " opacity-50 cursor-not-allowed"
			}
			if isChecked {
				checkedAttr = " checked"
			}
			fmt.Fprintf(&b,
				`<label data-filter-dimension=%q data-filter-option=%q data-filter-mode="include" data-option-count="%d"%s`+
					` class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm%s">`+
					`<span class="flex items-center gap-2">`+
					`<input type="checkbox" name="%s_in" value=%q%s%s />`+
					`<span class="font-medium text-slate-800">%s</span></span>`+
					`<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">%d</span></label>`,
				dim, option, optCount, excludedAttr, labelExtra,
				dim, option, checkedAttr, disabledAttr,
				capitalize(option), optCount,
			)
		}
		b.WriteString(`</div>`)

		// Exclude sub-section
		b.WriteString(`<div data-role="exclude-options" class="mt-2 space-y-1">`)
		b.WriteString(`<p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>`)
		for _, option := range options {
			isActive := contains(dimOut, option)
			impact := excCounts[option]
			activeAttr := ""
			checkedAttr := ""
			borderCls := "border-slate-200"
			if isActive {
				activeAttr = ` data-active="true"`
				checkedAttr = " checked"
				borderCls = "border-red-200 bg-red-50"
			}
			fmt.Fprintf(&b,
				`<label data-filter-dimension=%q data-filter-option=%q data-filter-mode="exclude" data-option-count="%d"%s`+
					` class="flex items-center justify-between rounded border %s px-3 py-2 text-sm">`+
					`<span class="flex items-center gap-2">`+
					`<input type="checkbox" name="%s_out" value=%q%s />`+
					`<span class="font-medium text-slate-800">%s</span></span>`+
					`<span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">%d</span></label>`,
				dim, option, impact, activeAttr, borderCls,
				dim, option, checkedAttr,
				capitalize(option), impact,
			)
		}
		b.WriteString(`</div>`)
		b.WriteString(`</section>`)
	}

	b.WriteString(`</div>`)
	return b.String()
}

func selectedAttr(current, value string) string {
	if current == value {
		return " selected"
	}
	return ""
}

func renderSortSelect(state QueryState) string {
	var b strings.Builder
	fmt.Fprintf(&b,
		`<select name="sort" data-role="sort-select" data-sort-order=%q`+
			` hx-get="/ui/reports/results" hx-target="#report-results"`+
			` hx-include="#report-filters"`+
			` class="rounded border border-slate-200 px-2 py-1 text-sm">`,
		state.Sort,
	)
	fmt.Fprintf(&b, `<option value="events_desc"%s>Events: high &#x2192; low</option>`, selectedAttr(state.Sort, "events_desc"))
	fmt.Fprintf(&b, `<option value="events_asc"%s>Events: low &#x2192; high</option>`, selectedAttr(state.Sort, "events_asc"))
	fmt.Fprintf(&b, `<option value="name_asc"%s>Name: A &#x2192; Z</option>`, selectedAttr(state.Sort, "name_asc"))
	b.WriteString(`</select>`)
	return b.String()
}

func renderResultsFragment(state QueryState) string {
	rows := sortRows(filterRows(state), state.Sort)
	n := len(rows)
	fp := fingerprint(state)
	var b strings.Builder

	fmt.Fprintf(&b,
		`<div id="result-count" hx-swap-oob="true" data-role="result-count" data-result-count="%d" `+
			`class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">%d results</div>`,
		n, n,
	)
	fmt.Fprintf(&b,
		`<section id="report-results" data-query-fingerprint=%q data-result-count="%d" data-search-query=%q data-sort-order=%q class="space-y-2">`,
		fp, n, state.Query, state.Sort,
	)
	fmt.Fprintf(&b, `<div data-role="active-filters" class="text-xs text-slate-500">%s</div>`, fp)
	b.WriteString(renderSortSelect(state))
	for _, row := range rows {
		fmt.Fprintf(&b,
			`<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id=%q>`+
				`<strong>%s</strong> <span class="text-slate-500">%s / %s / %s</span></div>`,
			row.ReportID, row.ReportID, row.Team, row.Status, row.Region,
		)
	}
	b.WriteString(`</section>`)
	return b.String()
}

func renderFullPage(state QueryState) string {
	panel := renderFilterPanel(state)
	rows := sortRows(filterRows(state), state.Sort)
	n := len(rows)
	fp := fingerprint(state)

	var b strings.Builder
	b.WriteString(`<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Reports</title>`)
	b.WriteString(`<script src="https://unpkg.com/htmx.org@1.9.10"></script>`)
	b.WriteString(`<script src="https://cdn.tailwindcss.com"></script></head>`)
	b.WriteString(`<body class="font-sans"><h1 class="text-xl font-bold p-4 border-b">Reports</h1>`)
	b.WriteString(`<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">`)
	b.WriteString(`<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">`)
	b.WriteString(`<aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">`)
	b.WriteString(panel)
	b.WriteString(`</aside>`)
	b.WriteString(`<main id="report-results-container" class="flex-1 overflow-y-auto p-4">`)
	fmt.Fprintf(&b,
		`<div id="result-count" data-role="result-count" data-result-count="%d" `+
			`class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">%d results</div>`,
		n, n,
	)
	b.WriteString(renderSortSelect(state))
	fmt.Fprintf(&b,
		`<section id="report-results" data-query-fingerprint=%q data-result-count="%d" data-search-query=%q data-sort-order=%q class="space-y-2">`,
		fp, n, state.Query, state.Sort,
	)
	for _, row := range rows {
		fmt.Fprintf(&b,
			`<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id=%q>`+
				`<strong>%s</strong></div>`,
			row.ReportID, row.ReportID,
		)
	}
	b.WriteString(`</section></main></div></form></body></html>`)
	return b.String()
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

func uiReports(c echo.Context) error {
	state := buildQueryState(c)
	return c.HTML(http.StatusOK, renderFullPage(state))
}

func uiReportsResults(c echo.Context) error {
	state := buildQueryState(c)
	return c.HTML(http.StatusOK, renderResultsFragment(state))
}

func uiReportsFilterPanel(c echo.Context) error {
	state := buildQueryState(c)
	return c.HTML(http.StatusOK, renderFilterPanel(state))
}

func healthz(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
}

func main() {
	e := echo.New()
	e.GET("/ui/reports", uiReports)
	e.GET("/ui/reports/results", uiReportsResults)
	e.GET("/ui/reports/filter-panel", uiReportsFilterPanel)
	e.GET("/healthz", healthz)
	e.Logger.Fatal(e.Start(":3000"))
}
