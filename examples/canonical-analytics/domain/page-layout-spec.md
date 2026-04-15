# Page Layout Specification

## Overview
Each view is a server-rendered HTML page. The layout is consistent across
all four implementations. Tailwind provides the utility classes.

## Chrome (consistent across all views)
- Top navigation bar: links to all 7 views, active view highlighted
- Page title: matches view name from spec.md
- Filter panel: left sidebar or collapsible top strip (implementation choice)
  - Multi-select inputs for: services, environment, severity (where applicable)
  - Date range inputs (date_from, date_to)
  - Submit button with hx-get and hx-target pointing at the main content panel
- Main content panel: chart panel + summary card (HTMX target)
- Footer: seed info (fixture profile name, seed value used, record counts)

## Filter Panel Requirements
- Multi-select filter controls must use native <select multiple> OR a
  Tailwind-styled checkbox list. Either is acceptable.
- Follow context/doctrine/filter-panel-rendering-rules.md if implementing
  include/exclude semantics. For the analytics examples, include-only is
  sufficient (full include/exclude is optional enhancement).
- Active filter state must be visually indicated (Tailwind: ring, bg, or badge).
- Submit must use hx-get (not POST) so filter state is URL-addressable.

## Chart Panel + Summary Card (HTMX fragment target)
The main panel contains:
  - Chart div: a <div id="chart-panel"> populated by Plotly.js from JSON
  - Summary card: key metrics (total count, date range, active filters)
  - For views with drilldown: a <div id="detail-panel"> populated by a
    separate HTMX request when user selects a chart element or table row

## Detail Panel (drilldown, optional per view)
- Rendered as a side panel or modal overlay
- Fragment endpoint: /fragments/details?view=<view>&item=<item>
- Returns: an HTML partial with detail metrics for the selected item

## Accessibility Minimum
- All filter inputs must have a visible or sr-only <label>
- Chart divs must have an aria-label describing the chart purpose
- Summary card text must be readable without interpreting the chart
