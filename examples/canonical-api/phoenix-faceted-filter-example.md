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

- `filter_rows/1` — applies all three dimensions; include = must be in _in if _in non-empty;
  exclude = must not be in _out if _out non-empty.
- `facet_counts/2` — for the target dimension, relaxes _in but keeps _out; applies all other
  dimensions fully.
- `exclude_impact_counts/2` — for each option: applies all other dimensions fully; applies
  target dimension's _out except the current option; ignores target dimension's _in.

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
all six state fields) and `data-result-count`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/phoenix-faceted-filter-example.ex`
- `examples/canonical-api/phoenix-faceted-filter-panel-template.html.heex`
