# Elixir Phoenix Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Elixir and Phoenix.
The filter panel HTML is rendered from HEEx templates. The backend computes all facet counts
and exclude-impact counts before passing them to the template as assigns.

## Language and rendering idiom

Elixir module with a `PhoenixFacetedFilterExample` namespace. HTML is built in two ways:

- `renderFilterPanel/1` uses `Enum.map_join/2` with heredoc string interpolation for
  programmatic rendering outside a live Phoenix context.
- `phoenix-faceted-filter-panel-template.html.heex` shows the idiomatic HEEx template
  pattern with `<%= for ... do %>` loops and conditional attribute lists.

Pattern matching on dimension name drives the facet count logic. Lists are normalized using
`Enum.uniq/1 |> Enum.sort/1` with `String.downcase/1` and `String.trim/1`.

## Filter logic

- `filter_rows/1` — calls `apply_text_search` first, then applies all three dimensions;
  include = must be in _in if _in non-empty; exclude = must not be in _out if _out non-empty.
- `facet_counts/2` — calls `apply_text_search` first (Q is never relaxed); for the target
  dimension, relaxes _in but keeps _out; applies all other dimensions fully.
- `exclude_impact_counts/2` — calls `apply_text_search` first; for each option: applies all
  other dimensions fully; applies target dimension's _out except the current option; ignores
  target dimension's _in.
- `apply_text_search/2` — filters rows by case-insensitive substring match on report_id;
  returns all rows when query is empty.
- `sort_rows/2` — sorts by sort value: `events_desc` (descending events, tiebreak report_id
  asc), `events_asc` (ascending events, tiebreak report_id asc), `name_asc` (ascending
  report_id). Sort never affects counts.

## Multi-value parameter parsing

Phoenix `conn.query_params["status_out"]` returns a single string for single values and
a list when multiple values share the same key. `normalize/1` accepts either and coerces
to a sorted, deduplicated list of lowercase strings.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: OOB result-count badge + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

All option elements carry the required data attributes:

- `data-filter-dimension` — dimension name (team, status, region)
- `data-filter-option` — option value (growth, platform, active, …)
- `data-filter-mode` — "include" or "exclude"
- `data-option-count` — integer count for include facet or exclude impact

Include options for an excluded value: `data-excluded="true"`, count=0, `opacity-50 cursor-not-allowed`, `disabled`.
Exclude options for an active value: `data-active="true"`, `border-red-200 bg-red-50`.

Quick exclude labels carry `data-role="quick-exclude"`, `data-quick-exclude-dimension`,
`data-quick-exclude-value`, `data-active`.

Results section carries `data-query-fingerprint` (deterministic sort-order fingerprint of
all eight state fields) and `data-result-count`.

**Search input** (at top of filter panel, above quick-excludes strip):
- `name="query"` — submitted with form; normalized to trimmed lowercase
- `data-role="search-input"` — identifies the search input element
- `data-search-query="{Q}"` — reflects current query value for client reads

**Sort select** (in results section, below result-count badge, above result cards):
- `name="sort"` — submitted with form; valid values: `events_desc`, `events_asc`, `name_asc`
- `data-role="sort-select"` — identifies the sort control element
- `data-sort-order="{sort}"` — reflects current sort value; option `selected` attribute set
  to prevent dropdown reset on HTMX swaps

**Results section** (`id="report-results"`) additional attributes:
- `data-search-query="{Q}"` — current text search query
- `data-sort-order="{sort}"` — current sort order

**Layout wrapper** (`id="reports-layout"`):
- `data-role="reports-layout"` — identifies the independent scroll layout container
- Structure: `<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">`
  with `<aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">`
  and `<main id="report-results-container" class="flex-1 overflow-y-auto p-4">`

**State fields** `query` and `sort` are now part of `QueryState` (8 total fields). Both are
included in the fingerprint as `|query={Q}|sort={sort}` at the end of the fingerprint string.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/phoenix-faceted-filter-example.ex`
- `examples/canonical-api/phoenix-faceted-filter-panel-template.html.heex`
