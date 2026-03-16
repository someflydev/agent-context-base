# Ruby Hanami Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using Ruby and Hanami.
HTML is rendered server-side using `<<~HTML` heredoc interpolation inside a `FilterService`
module. The example follows Hanami's action-based architecture with a shared service layer.

## Language and rendering idiom

Single `.rb` file with `FilterService` module and `Hanami::Action` subclasses. HTML is
assembled via `<<~HTML` heredocs with `#{}` string interpolation. `Array.join` flattens
per-option HTML strings.

`QueryState` is a Ruby `Struct` with six `Array` fields. `normalize` uses `uniq` and `sort`
after `strip.downcase`. The `FilterService` module contains all pure filter functions as
module methods.

## Filter logic

- `filter_rows(state)` — `select` with `matches_dim` per dimension.
- `facet_counts(state, dim)` — per-dimension case dispatch; relaxes _in, keeps _out for
  target; applies all other dimensions fully.
- `exclude_impact_counts(state, dim)` — per option: other dims fully; target _out minus
  current option; _in ignored.

## Multi-value parameter parsing

Hanami/Rack `params[:status_out]` may return a `String` or `Array` depending on the
request. `normalize` wraps non-array values with `Array()` before dedup and sort.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page with filter panel and results |
| GET | /ui/reports/results | HTMX partial: OOB result-count badge + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

## Data contract

All option elements carry `data-filter-dimension`, `data-filter-option`, `data-filter-mode`,
`data-option-count`. Include options for excluded values: `data-excluded="true"`, count=0,
`disabled`. Exclude options for active values: `data-active="true"`, red styling.

Quick exclude labels carry `data-role="quick-exclude"`, `data-quick-exclude-dimension`,
`data-quick-exclude-value`, `data-active`.

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-api/ruby-hanami-faceted-filter-example.rb`
