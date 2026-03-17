# Faceted Filter Panel — Cross-Language Correctness Reference

This document describes the shared dataset, algorithm contract, and HTML data-* attribute
contract that all 14 faceted filter panel examples implement identically. It serves as the
authoritative cross-language correctness reference for the split include/exclude filter
panel pattern.

---

## Shared Dataset

All examples use the same six-row in-memory dataset:

| report_id         | team     | status   | region | events |
|-------------------|----------|----------|--------|--------|
| daily-signups     | growth   | active   | us     | 12     |
| trial-conversions | growth   | active   | us     | 7      |
| api-latency       | platform | paused   | eu     | 5      |
| checkout-failures | growth   | active   | eu     | 9      |
| queue-depth       | platform | active   | apac   | 11     |
| legacy-import     | platform | archived | us     | 4      |

**Dimension options:**
- `team`: growth, platform
- `status`: active, paused, archived
- `region`: us, eu, apac

**Quick excludes (backend constant):**
```
[("status", "archived"), ("status", "paused")]
```

---

## QueryState Model

Eight fields. Six filter lists (sorted deduplicated lowercase strings) plus two scalar fields:

```
team_in, team_out, status_in, status_out, region_in, region_out, query, sort
```

- `query`: single string, trimmed and lowercased. Default: `""`.
- `sort`: single string, validated against allowed values. Default: `"events_desc"`.
  Allowed values: `"events_desc"`, `"events_asc"`, `"name_asc"`.

Multi-value query params (`?status_out=archived&status_out=paused`) are parsed as a list.
Each filter field is normalized: `strip()`, `lower()`, `dedup`, `sort`.

---

## Filter Algorithms

### apply_text_search(rows, query)

Case-insensitive substring match on `report_id`. Returns all rows when `query` is empty.
**Must be called first** in `filter_rows`, `facet_counts`, and `exclude_impact_counts`.
Q is never relaxed.

```
if query == "": return rows
return [r for r in rows if query in r.report_id.lower()]
```

### filter_rows(state)

1. `apply_text_search(rows, state.query)` — Q applied first.
2. For each remaining row, apply all three dimensions:

```
include: if D_in non-empty → row[dim] must be in D_in
exclude: if D_out non-empty → row[dim] must not be in D_out
```

3. `sort_rows(filtered, state.sort)` — sort applied last (display order only).

### facet_counts(state, dimension)

For the **include** sub-section. Per option in the dimension:
1. `apply_text_search(rows, state.query)` — Q applied first, never relaxed.
2. Apply all **other** dimensions fully (both _in and _out).
3. For the **target** dimension: relax _in (ignore it), keep _out applied.
4. Count rows where `row[dim] == option`.

This answers: "how many rows include this option given the current cross-filters and search?"

### exclude_impact_counts(state, dimension)

For the **exclude** sub-section. Per option in the dimension:
1. `apply_text_search(rows, state.query)` — Q applied first.
2. Apply all **other** dimensions fully (both _in and _out).
3. For the **target** dimension: apply _out **except** the current option; ignore _in entirely.
4. Count rows where `row[dim] == option`.

This answers: "how many rows would this exclusion currently remove?"

### sort_rows(rows, sort_value)

Sort the result list only — never called inside count functions.

| `sort` value | Behaviour |
|---|---|
| `events_desc` | Numeric descending by `events`; tiebreak: `report_id` ascending |
| `events_asc` | Numeric ascending by `events`; tiebreak: `report_id` ascending |
| `name_asc` | Lexicographic ascending by `report_id` |

With `sort=events_asc`: first row is `legacy-import` (events: 4).
With `sort=name_asc`: first row is `api-latency` (alphabetically first).

### fingerprint(state)

Deterministic string for tracking query state across HTMX swaps:

```
team_in=...|team_out=...|status_in=...|status_out=...|region_in=...|region_out=...|query={Q}|sort={sort}
```

Values are the sorted lists joined with commas.

---

## Reference Count Table (no filters, no search active)

With empty state (all filters unset, query=""):

| Dimension | Option   | facet_count | exclude_impact |
|-----------|----------|-------------|----------------|
| team      | growth   | 3           | 3              |
| team      | platform | 3           | 3              |
| status    | active   | 4           | 4              |
| status    | paused   | 1           | 1              |
| status    | archived | 1           | 1              |
| region    | us       | 3           | 3              |
| region    | eu       | 2           | 2              |
| region    | apac     | 1           | 1              |

Total rows: 6.

### Reference Count Table with query="daily" active

Only `daily-signups` matches. Counts reflect search-narrowed dataset:

| Dimension | Option   | facet_count |
|-----------|----------|-------------|
| team      | growth   | 1           |
| team      | platform | 0           |
| status    | active   | 1           |
| status    | paused   | 0           |
| status    | archived | 0           |
| region    | us       | 1           |
| region    | eu       | 0           |
| region    | apac     | 0           |

Total rows: 1.

---

## HTML Data-* Attribute Contract

All option `<label>` elements must carry:

| Attribute | Value |
|-----------|-------|
| `data-filter-dimension` | dimension name (team, status, region) |
| `data-filter-option` | option value (growth, active, us, …) |
| `data-filter-mode` | "include" or "exclude" |
| `data-option-count` | integer count |

**Include option rules:**
- If the option is in D_out (currently excluded):
  - `data-option-count` must be 0
  - `data-excluded="true"` must be present
  - Label must have `opacity-50 cursor-not-allowed`
  - Checkbox must have `disabled`

**Exclude option rules:**
- If the option is in D_out (currently active):
  - `data-active="true"` must be present
  - Label must have `border-red-200 bg-red-50` styling

**Quick exclude labels:**

| Attribute | Value |
|-----------|-------|
| `data-role` | "quick-exclude" |
| `data-quick-exclude-dimension` | dimension name |
| `data-quick-exclude-value` | option value |
| `data-active` | "true" or "false" |

**Search input:**
- `data-role="search-input"`, `name="query"`, `data-search-query`, `hx-trigger="keyup changed delay:300ms"`

**Sort select:**
- `data-role="sort-select"`, `name="sort"`, `data-sort-order`; option `selected` reflects current `state.sort`

**Results section:**
- `id="report-results"`, `data-query-fingerprint`, `data-result-count`, `data-search-query`, `data-sort-order`

**OOB result-count badge:**
- `id="result-count"`, `hx-swap-oob="true"`, `data-role="result-count"`, `data-result-count`

**Layout wrapper (full page only — never a swap target):**
- `data-role="reports-layout"`, `id="reports-layout"`, `class="flex h-screen overflow-hidden"`
- `#filter-panel`: `class="w-72 flex-shrink-0 overflow-y-auto border-r p-4"` (search input lives here)
- `#report-results-container`: `class="flex-1 overflow-y-auto p-4"` (sort select and results live here)

---

## Endpoints (all implementations)

| Method | Path | Description |
|--------|------|-------------|
| GET | /ui/reports | Full dashboard page |
| GET | /ui/reports/results | HTMX partial: OOB badge + results section |
| GET | /ui/reports/filter-panel | HTMX partial: filter panel only |
| GET | /healthz | Health check |

---

## Language Implementations

| Language | Framework | File |
|----------|-----------|------|
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

Template files (where required by the framework):

| Language | Template file |
|----------|--------------|
| Elixir | `phoenix-faceted-filter-panel-template.html.heex` |
| Go | `go-echo-faceted-filter-panel-template.templ` |
| Zig | `zig-zap-jetzig-faceted-filter-panel-template.zmpl` |

---

## Key Differences by Language

### Multi-value parameter parsing

Each language has its own mechanism for `?status_out=archived&status_out=paused`:

| Language | Mechanism |
|----------|-----------|
| Python | `request.query_params.getlist("status_out")` |
| Elixir | `conn.query_params["status_out"]` (list or string) |
| Go | `c.QueryParams()["status_out"]` ([]string) |
| TypeScript | `searchParams.getAll("status_out")` |
| Rust | `#[serde(default)] Vec<String>` on FilterQuery |
| Ruby | `Array(params[:status_out])` |
| Clojure | `(get-in request [:query-params "status_out"])` |
| Kotlin | `request.queries("status_out")` |
| Scala | `req.multiParams.getOrElse("status_out", Nil)` |
| Crystal | `env.request.query_params.fetch_all("status_out")` |
| Dart | `uri.queryParametersAll["status_out"]` |
| OCaml | `Dream.queries request "status_out"` |
| Nim | Manual raw query string split on `&` |
| Zig | Single-value only (see file note) |

### HTML building idiom

| Language | Approach |
|----------|----------|
| Python | f-string / join |
| Elixir | Enum.map_join / HEEx template |
| Go | strings.Builder / templ components |
| TypeScript | Template literals / Array.join |
| Rust | String::push_str / format! |
| Ruby | <<~HTML heredoc / Array.join |
| Clojure | Hiccup2 nested vectors |
| Kotlin | buildString { append } |
| Scala | s"""...""" / mkString |
| Crystal | String.build { \|io\| io << } |
| Dart | StringBuffer |
| OCaml | TyXML combinators |
| Nim | fmt strings / &= |
| Zig | Zmpl template / {{variable}} |

---

## Related

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/filter-state-and-query-state.md`
- `context/doctrine/search-sort-scroll-layout.md`
- `context/workflows/render-filter-panel-include-exclude-ui.md`
- `context/workflows/add-text-search-to-filter-ui.md`
- `context/workflows/add-sort-order-to-results.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
- `examples/canonical-integration-tests/playwright-search-sort-example.spec.ts`
