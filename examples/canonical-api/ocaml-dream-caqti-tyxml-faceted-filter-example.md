# OCaml Dream/TyXML Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using OCaml, Dream, and
TyXML. HTML is rendered server-side using TyXML combinators. The filter pipeline uses
OCaml's strong type system with record types and pure functions.

## Language and rendering idiom

Single `.ml` file. `report_row` and `query_state` are OCaml record types with labeled
fields. `query_state` now includes `query: string` and `sort: string` fields. HTML is
built with TyXML's `Tyxml.Html` module using typed combinators like `div`, `label`,
`input`, `span`, `select`, `option`.

Data-* attributes use `Tyxml.Html.Unsafe.string_attrib "data-filter-dimension" value`
since TyXML does not have a typed representation for arbitrary data attributes.

`normalize` uses `List.sort_uniq String.compare` after `String.lowercase_ascii` and
`String.trim`. `normalize_sort` validates against the three allowed sort values.

## Filter logic

- `apply_text_search rows q` — `List.filter` using a manual `contains` helper (no Str
  dependency); returns all rows when `q` is empty. Called first in all three filter
  functions.
- `filter_rows state` — calls `apply_text_search` first, then `List.filter` with
  `matches_dim` per dimension, then `sort_rows`.
- `facet_counts state dim` — calls `apply_text_search` first; pattern match on dim;
  relaxes _in, keeps _out for target; applies all other dimensions fully. Returns
  association list of `(string * int)`. Sort never affects counts.
- `exclude_impact_counts state dim` — calls `apply_text_search` first; per option: other
  dims fully; target _out minus current option; _in ignored.
- `sort_rows rows sort_val` — `List.sort` with a comparator dispatched on `sort_val`:
  `events_desc` (default), `events_asc`, `name_asc`; event sorts tiebreak by `report_id`.

## Substring search

`contains s sub` is implemented manually using `String.sub` comparisons without the Str
module. A production implementation may use `Str.string_match` or the Re library.

## Multi-value parameter parsing

`Dream.queries request "status_out"` returns `string list` with all values for repeated
keys. `normalize` deduplicates and sorts.

Single-value params `query` and `sort` use `Dream.query request key |> Option.value ~default:""`.

## Rendering additions

**Search input** — rendered at top of filter panel via TyXML `input` element with
`hx-trigger="keyup changed delay:300ms"`.

**Sort select** — `render_sort_select state` builds a TyXML `select` with conditional
`a_selected ()` attrs: `if state.sort = v then [a_selected ()] else []`.

**Independent scroll layout** — full page uses
`<div data-role="reports-layout" class="flex h-screen overflow-hidden">` with
`<aside class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">` and
`<main class="flex-1 overflow-y-auto p-4">`.

**Results section** carries `data-search-query` and `data-sort-order` attributes.

## Fingerprint

`"query=" ^ state.query` and `"sort=" ^ state.sort` appended at the end of the
fingerprint list passed to `String.concat "|"`.

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

Results section: `id="report-results"`, `data-query-fingerprint`, `data-result-count`,
`data-search-query`, `data-sort-order`.
OOB badge: `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`.
Search input: `data-role="search-input"`, `data-search-query`.
Sort select: `data-role="sort-select"`, `data-sort-order`.

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/ocaml-dream-caqti-tyxml-faceted-filter-example.ml`
