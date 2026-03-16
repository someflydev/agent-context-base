# OCaml Dream/TyXML Faceted Filter Example

## Purpose

Demonstrates the full split include/exclude filter panel pattern using OCaml, Dream, and
TyXML. HTML is rendered server-side using TyXML combinators. The filter pipeline uses
OCaml's strong type system with record types and pure functions.

## Language and rendering idiom

Single `.ml` file. `report_row` and `query_state` are OCaml record types with labeled
fields. HTML is built with TyXML's `Tyxml.Html` module using typed combinators like
`div`, `label`, `input`, `span`.

Data-* attributes use `Tyxml.Html.Unsafe.string_attrib "data-filter-dimension" value`
since TyXML does not have a typed representation for arbitrary data attributes.

`normalize` uses `List.sort_uniq String.compare` after `String.lowercase_ascii` and
`String.trim`.

## Filter logic

- `filter_rows state` — `List.filter` with `matches_dim` per dimension.
- `facet_counts state dim` — pattern match on dim; relaxes _in, keeps _out for target;
  applies all other dimensions fully. Returns association list of `(string * int)`.
- `exclude_impact_counts state dim` — per option: other dims fully; target _out minus
  current option; _in ignored.

## Multi-value parameter parsing

`Dream.queries request "status_out"` returns `string list` with all values for repeated
keys. `normalize` deduplicates and sorts.

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
- `examples/canonical-api/ocaml-dream-caqti-tyxml-faceted-filter-example.ml`
