# Search, Sort, and Scroll Layout

Authoritative reference for three UI enhancements added to the backend-driven faceted
filter pattern (PROMPT_64): text search, sort order, and independent scroll layout.

---

## Text Search in Faceted Filter UIs (RULE 4)

### When to use text search

Add a text search bar when the result set is large enough that users need free-text
narrowing beyond what dimension facets provide. Search complements facets; it does not
replace them.

### Why search must narrow the base row set before facet logic runs

Text search is a **base filter**. It is applied to the full row set before any facet
dimension logic executes. Every subsequent computation — `filter_rows`, `facet_counts`,
`exclude_impact_counts` — operates on the search-narrowed row set.

This ordering is non-negotiable. If facet counts are computed against the pre-search
dataset when a search is active, each option count will claim more rows than actually
exist in the visible result set. A user searching for "signup" who sees "platform: 3"
in the team facet will be confused to find only 1 result. The counts would be lying.

### How text search interacts with facet_counts

`facet_counts(state, dimension)` relaxes the same-dimension includes so users can see
how many rows each option would add. It does **not** relax the text search. Concretely:

1. Apply Q (text search) to the full row set — this is always applied.
2. Apply all OTHER dimension filters fully (both _in and _out).
3. For the TARGET dimension: apply its _out but relax its _in (the standard facet-count relaxation).
4. Count rows per option value.

Search is part of the "always-on" filter layer, not the "relaxable" layer.

### How text search interacts with exclude_impact_counts

`exclude_impact_counts(state, dimension)` counts how many rows a given exclusion removes.
Text search is applied first here too:

1. Apply Q to the full row set.
2. Apply all OTHER dimensions fully (both _in and _out).
3. For the TARGET dimension: apply its _out EXCEPT the current option; ignore _in.
4. Count rows where row[dimension] == option.

### The failure mode: computing counts against the pre-search dataset

When Q is active and facet counts are computed against the full dataset:

- Option counts will be larger than the result set permits.
- Users will click a facet option expecting N more rows but get fewer.
- The result-count badge and facet option counts will disagree.

This is a **correctness failure**, not a cosmetic one.

### Data-* contract for the search input

```
name="query"
data-role="search-input"
data-search-query="{current Q value, empty string if none}"
hx-trigger="keyup changed delay:300ms"
hx-get="/ui/reports/results"
hx-target="#report-results"
hx-include="#report-filters"
```

The input must be **inside** the HTMX form (`id="report-filters"`) so that typing triggers
partial updates. It must be pre-populated with the current Q value on every render (full
page and filter panel fragment) so that the input does not reset to empty on HTMX swaps.

The `delay:300ms` debounce is required. Without it, every keystroke sends a request,
flooding the server on fast typing.

---

## Sort Order (RULE 5)

### What sort controls

Sort controls the **display order** of result rows. It has no effect on any counts:
not the result-count badge, not facet option counts, not exclude impact counts.

If sort appears to affect counts, the implementation is wrong.

### The three canonical sort options

| Query param value | Label            | Logic                               |
|-------------------|------------------|-------------------------------------|
| `events_desc`     | Events: high → low | Numeric descending by events (default) |
| `events_asc`      | Events: low → high | Numeric ascending by events         |
| `name_asc`        | Name: A → Z      | Lexicographic ascending by report_id |

When the `sort` parameter is absent or has an unrecognised value, default to `events_desc`.
When events counts are equal, use `report_id` as a stable tiebreaker.

### Why sort must be preserved in the fragment response

On every HTMX partial swap, the results fragment is re-rendered. The sort select element
is inside the fragment. If the select is not pre-populated with the current sort value,
it resets to the first option on every swap. A user who selected `name_asc` and then
clicks a facet checkbox would see the sort dropdown jump back to `events_desc`.

To prevent this: always read the `sort` value from state when rendering the select, and
add `selected` to the matching option.

### Data-* contract for the sort select

```
name="sort"
data-role="sort-select"
data-sort-order="{current sort value}"
```

The select must be inside the HTMX form. It is rendered in the results section header,
below the result-count badge and above the result list. It must also appear in the results
fragment (not just the full page) so that HTMX swaps preserve the selected value.

Additionally, add `data-sort-order="{sort}"` to the `id="report-results"` element so
Playwright assertions can verify the sort state without needing to inspect the select.

---

## Independent Scroll Layout (RULE 6)

### The layout constraint

The filter panel and results section must scroll independently. When the user scrolls
the filter panel to find a facet option, the results section must not scroll. When the
user scrolls the results to review row cards, the filter panel must not scroll.

Coupled scroll (where the entire page scrolls as one unit) makes this interaction
impossible and degrades usability for any result set larger than one screen.

### The CSS approach

No JavaScript is required. Pure CSS achieves independent scroll:

```html
<!-- Outermost wrapper: horizontal flex, fixed viewport height, no overflow -->
<div data-role="reports-layout" class="flex h-screen overflow-hidden" id="reports-layout">

  <!-- Filter panel: fixed width, independent vertical scroll -->
  <aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">
    <!-- filter panel contents -->
  </aside>

  <!-- Results container: remaining width, independent vertical scroll -->
  <main id="report-results-container" class="flex-1 overflow-y-auto p-4">
    <!-- result-count badge -->
    <!-- sort select -->
    <section id="report-results" ...>
      <!-- result cards -->
    </section>
  </main>

</div>
```

Key properties:
- `h-screen overflow-hidden` on the wrapper locks the layout to the viewport height and
  prevents the outermost element from scrolling.
- `overflow-y-auto` on both columns creates independent scroll contexts.
- `flex-shrink-0` on the filter panel prevents it from collapsing.

### Why the layout wrapper must NOT be a partial swap target

HTMX partial swaps replace only `id="report-results"` (and OOB-swap the result-count
badge). The layout wrapper (`data-role="reports-layout"`) is rendered **once** on full
page load and is never replaced.

If the layout wrapper were a swap target, every filter change would:
1. Re-render the entire page structure.
2. Reset both scroll positions to zero.
3. Lose any scroll state the user had built up.

**Only** `id="report-results"` is the swap target. Everything outside it is static after
the initial page load.

### Why this matters

Users commonly:
- Scroll the filter panel down to find a less-common facet option.
- While the results section is scrolled to row 15.
- Then click the option to apply it.

If the scroll positions are coupled, clicking the option resets both to zero and the user
loses their place in both panels.

### Data-* contract for the layout wrapper

```
data-role="reports-layout"
id="reports-layout"
class="flex h-screen overflow-hidden"
```

The `data-role="reports-layout"` attribute is used by Playwright assertions to locate the
wrapper and verify its CSS state and child structure.

---

## Common Failure Modes

| Failure | Consequence |
|---|---|
| Recomputing facet counts against the pre-search dataset when Q is active | Counts lie: show more rows than actually exist in the search-filtered result set |
| Relaxing text search in `facet_counts` the same way same-dimension includes are relaxed | Same as above; search must never be relaxed |
| Resetting the sort dropdown to `events_desc` on every HTMX swap | User's sort selection is lost on every facet change |
| Making the layout wrapper a swap target | Scroll positions reset on every filter update |
| Omitting `data-search-query` on the search input | Playwright assertions cannot verify Q was preserved after a swap |
| Omitting `data-sort-order` on the sort select or results section | Playwright assertions cannot verify sort state without parsing visible text |
| Forgetting to include `query` and `sort` in the fingerprint | Fragment verification cannot confirm state round-trips correctly |
| Not pre-populating the search input value from state | Input clears on every HTMX swap, losing the user's search term |
| Forgetting `delay:300ms` on `hx-trigger="keyup changed"` | Every keystroke sends a server request; floods the server on fast typing |

---

## Related

- `context/doctrine/faceted-query-count-discipline.md` — count correctness rules including text search section
- `context/doctrine/filter-state-and-query-state.md` — state model including query and sort fields
- `context/doctrine/filter-panel-rendering-rules.md` — rendering rules for search input, sort select, and layout
- `context/workflows/add-text-search-to-filter-ui.md`
- `context/workflows/add-sort-order-to-results.md`
- `examples/canonical-api/fastapi-search-sort-filter-example.py`
