# Add Text Search to Filter UI

## Purpose

Add a text search bar that narrows results and counts on top of any active facet filters,
following RULE 4 from `context/doctrine/search-sort-scroll-layout.md`.

## When to use it

- When the result set is large enough that users need free-text narrowing.
- When the filter panel alone does not give sufficient precision.
- When users need to locate a specific named item quickly without knowing its dimension values.

## Sequence

1. **Add a `query` field to the query state struct/type.** Default to empty string.
   Normalize by trimming whitespace and lowercasing. An empty string after trimming is
   treated as absent (no search active).

2. **Implement `apply_text_search(rows, query)` as a standalone function.** Filter a row
   list by case-insensitive substring match on `report_id` (at minimum). If the
   implementation also matches other string fields (team, status, region), it must do so
   consistently and document which fields are searched.

   ```python
   def apply_text_search(rows, query):
       if not query:
           return rows
       q = query.lower()
       return [r for r in rows if q in r["report_id"].lower()]
   ```

3. **Update `filter_rows`**: call `apply_text_search` first, then apply dimension filters
   to the narrowed set.

4. **Update `facet_counts`**: call `apply_text_search` first (on the pre-dimension-relaxation
   set). Q is never relaxed — it applies before any facet-count dimension relaxation.

5. **Update `exclude_impact_counts`**: call `apply_text_search` first, before applying
   other-dimension filters and counting.

6. **Add the search input element** inside the HTMX form with:
   ```html
   <input type="text" name="query" value="{Q}"
          placeholder="Search reports…"
          data-role="search-input"
          data-search-query="{Q}"
          hx-get="/ui/reports/results"
          hx-target="#report-results"
          hx-trigger="keyup changed delay:300ms"
          hx-include="#report-filters" />
   ```
   Place it at the top of the filter panel, above the quick-excludes strip.
   Pre-populate `value` and `data-search-query` from the current Q state.

7. **Add `query` to the fingerprint string:**
   ```
   team_in=...|...|region_out=...|query={Q}|sort={sort}
   ```

8. **Add `data-search-query="{Q}"` to the results section element** (`id="report-results"`).

9. **Write Playwright assertions verifying:**
   - With `query="daily"`: result count = 1 (daily-signups only).
   - Facet option counts reflect the search-narrowed set (growth=1, platform=0, active=1, etc.).
   - The search input `value` attribute is preserved after an HTMX swap triggered by a
     facet filter change.
   - The `data-search-query` attribute on `#report-results` matches the active query.

## Outputs

- Updated query state model (new `query` field).
- `apply_text_search` helper function.
- Updated `filter_rows`, `facet_counts`, `exclude_impact_counts` calling `apply_text_search`.
- Search input in the rendered HTML with all required data-* attributes.
- Updated fingerprint string including `query`.
- Playwright tests for search + count accuracy.

## Related doctrine

- `context/doctrine/search-sort-scroll-layout.md`
- `context/doctrine/faceted-query-count-discipline.md` (Text Search as Base Filter section)

## Common pitfalls

- **Computing facet counts against the full dataset when Q is active.** This causes count
  mismatch: option counts show more rows than exist in the search-filtered result set.
- **Not pre-populating the search input `value` attribute.** The input resets to empty
  on every HTMX swap if the value is not set from state.
- **Missing `data-search-query` on the input or results section.** Playwright assertions
  rely on this attribute to verify Q was preserved.
- **Using `hx-trigger="keyup"` without `delay:300ms`.** This floods the server on fast
  typing. The debounce is required.
- **Relaxing Q in `facet_counts`.** Q must never be relaxed. Only same-dimension includes
  are relaxed in the facet-count path.

## Stop conditions

- A Playwright test passes: with `query="daily"`, result count = 1 and facet counts
  reflect only the matching row.
- The search input `value` attribute is preserved after an HTMX partial swap triggered
  by a facet filter checkbox change.
- `#report-results[data-search-query]` reflects the active query on every partial swap.
