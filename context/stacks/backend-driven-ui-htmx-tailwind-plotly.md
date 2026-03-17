# Backend-Driven UI: HTMX + Tailwind + Plotly

Use this pack when a backend service renders interactive HTML fragments, count surfaces, and chart payloads without introducing a frontend application framework.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- route or controller modules for pages, fragments, and chart data
- template or HTML-render helper files
- query services that own filter parsing and count semantics
- Playwright specs for backend-driven UI behavior
- focused backend tests for count and aggregation correctness

## Common Change Surfaces

- normalized query-state parsing
- HTMX fragment endpoints and out-of-band swaps
- Tailwind-backed filter and result markup with stable selectors
- Plotly data endpoints derived from live query results
- Playwright flows that verify rows, counts, and chart alignment

## Testing Expectations

- verify result rows and result count from the same query state
- verify representative facet counts under include and exclude filters
- verify chart payload alignment with the visible result state
- verify one or two backend-driven user flows with Playwright

## Split Include/Exclude Filter Panel

Backend-driven filter panels must split include and exclude options into distinct
sub-sections per dimension group. A single merged list cannot express both modes
without ambiguity.

**Structure per dimension group:**
1. Include sub-section — one labeled checkbox per option, with include/facet count.
2. Exclude sub-section — one labeled checkbox per option, with exclude impact count.

**Key rules:**
- When a value is in D_out (excluded), its include option must show count 0, carry
  `data-excluded="true"`, and render as greyed/disabled (`opacity-50 cursor-not-allowed`,
  `disabled` on the checkbox). Its exclude option must remain visually normal.
- The exclude impact count (`exclude_impact_counts(state, dimension)`) is distinct from
  `facet_counts`. It answers "how many rows does this exclusion currently remove?"
- A quick-excludes strip may appear above the dimension groups. It is declared via a
  `QUICK_EXCLUDES` backend constant and mirrors the state of the corresponding exclude
  options in the main section. Both share the same `name`/`value` form inputs.

**Data-* attribute contract (all option elements must carry these):**
```
Include option: data-filter-dimension, data-filter-option, data-filter-mode="include",
                data-option-count (0 when excluded), data-excluded="true" (when in D_out)
Exclude option: data-filter-dimension, data-filter-option, data-filter-mode="exclude",
                data-option-count (impact count), data-active="true" (when in D_out)
Quick exclude:  data-role="quick-exclude", data-quick-exclude-dimension,
                data-quick-exclude-value, data-active="true"/"false"
```

These attributes are the verification contract for Playwright tests and backend unit tests.

See `context/doctrine/filter-panel-rendering-rules.md` for the full specification and
failure mode table. See `examples/canonical-api/fastapi-split-filter-panel-example.py`
for a complete working implementation.

## Search, Sort, and Independent Scroll Layout (PROMPT_64)

All 14 language implementations have been extended with three additional features:

- **Text search (RULE 4)**: A free-text search input in the filter panel that narrows results
  and facet counts before any facet logic runs. `apply_text_search` is called first in
  `filter_rows`, `facet_counts`, and `exclude_impact_counts`. Q is never relaxed.
- **Sort order (RULE 5)**: A sort select in the results header that controls display order
  only. `sort_rows` is never called inside count functions. Options: `events_desc` (default),
  `events_asc`, `name_asc`. The selected option is pre-populated per state to survive HTMX swaps.
- **Independent scroll layout (RULE 6)**: CSS-only layout with `flex h-screen overflow-hidden`
  wrapper, `overflow-y-auto` on `#filter-panel` (sidebar) and `#report-results-container`
  (main). The wrapper is never a swap target.

**New data-* attributes added:**
- Search input: `data-role="search-input"`, `data-search-query`
- Sort select: `data-role="sort-select"`, `data-sort-order`
- Results section: `data-search-query`, `data-sort-order` (added to existing `id="report-results"`)
- Layout wrapper: `data-role="reports-layout"`

**Reference implementation:** `examples/canonical-api/fastapi-search-sort-filter-example.py`
**Playwright test suite:** `examples/canonical-integration-tests/playwright-search-sort-example.spec.ts`
**Doctrine:** `context/doctrine/search-sort-scroll-layout.md`

## Multi-Language Support

The split include/exclude filter panel pattern (plus text search, sort, and scroll layout)
is implemented identically across 14 language stacks. All implementations share the same
in-memory dataset, QueryState model, filter algorithm, HTML data-* attribute contract,
and endpoint structure.

**Language implementations (all in `examples/canonical-api/`):**

| Language | Framework | Example file |
|----------|-----------|-------------|
| Python | FastAPI | `fastapi-search-sort-filter-example.py` |
| Elixir | Phoenix | `phoenix-faceted-filter-example.ex` |
| Go | Echo + templ | `go-echo-faceted-filter-example.go` |
| TypeScript | Hono + Bun | `typescript-hono-faceted-filter-example.ts` |
| Rust | Axum | `rust-axum-faceted-filter-example.rs` |
| Ruby | Hanami | `ruby-hanami-faceted-filter-example.rb` |
| Clojure | Kit + Hiccup | `clojure-kit-nextjdbc-hiccup-faceted-filter-example.clj` |
| Kotlin | http4k | `kotlin-http4k-exposed-faceted-filter-example.kt` |
| Scala | http4s + ZIO | `scala-tapir-http4s-zio-faceted-filter-example.scala` |
| Crystal | Kemal | `crystal-kemal-avram-faceted-filter-example.cr` |
| Dart | Dart Frog | `dart-dartfrog-faceted-filter-example.dart` |
| OCaml | Dream + TyXML | `ocaml-dream-caqti-tyxml-faceted-filter-example.ml` |
| Nim | Jester | `nim-jester-happyx-faceted-filter-example.nim` |
| Zig | Jetzig + Zap | `zig-zap-jetzig-faceted-filter-example.zig` |

See `examples/canonical-api/README-faceted-filter-examples.md` for the cross-language
correctness reference including shared dataset, algorithm contract, and multi-value param
parsing idioms per language.

## Common Assistant Mistakes

- treating HTMX responses as lightweight text instead of a contract surface
- computing chart data separately from the filtered result query
- relying on frontend state to infer filters the backend never normalized
- writing Playwright specs that prove clicks but not semantics
- showing non-zero include counts for excluded values (trust failure, not cosmetic)
- deriving the exclude impact count from the facet_counts path (returns wrong values)
- greying the exclude option instead of (or in addition to) the include option
