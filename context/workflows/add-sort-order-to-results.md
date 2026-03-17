# Add Sort Order to Results

## Purpose

Add a sort order dropdown to the results section that controls result ordering without
affecting any counts, following RULE 5 from `context/doctrine/search-sort-scroll-layout.md`.

## When to use it

- Any time the results section contains ordered rows that users may want to re-sort
  without changing the active filter state.
- When users need to find the highest/lowest-value items or browse alphabetically.

## Sequence

1. **Add a `sort` field to the query state struct/type.** Default to `"events_desc"`.
   Accept values: `"events_desc"`, `"events_asc"`, `"name_asc"`. Treat any other value
   as `"events_desc"`.

2. **Implement `sort_rows(rows, sort_value)` as a standalone function** that returns a
   new sorted list:
   - `"events_desc"` → numeric descending by `events` field.
   - `"events_asc"`  → numeric ascending by `events` field.
   - `"name_asc"`    → lexicographic ascending by `report_id` (or equivalent identifier).
   - Unknown value   → same as `"events_desc"`.

   Use `report_id` as a stable tiebreaker when `events` values are equal.

3. **Apply `sort_rows` in results rendering.** Call it on the filtered row list immediately
   before building result card HTML. Never call it inside count functions.

4. **Add the sort select element** inside the HTMX form in the results section header:
   ```html
   <select name="sort"
           data-role="sort-select"
           data-sort-order="{current sort value}"
           hx-get="/ui/reports/results"
           hx-target="#report-results"
           hx-include="#report-filters">
     <option value="events_desc" {selected if sort==events_desc}>Events: high → low</option>
     <option value="events_asc"  {selected if sort==events_asc}>Events: low → high</option>
     <option value="name_asc"    {selected if sort==name_asc}>Name: A → Z</option>
   </select>
   ```
   Position: below the result-count badge, above the result list.

5. **Add `sort` to the fingerprint string:**
   ```
   ...|query={Q}|sort={sort}
   ```

6. **Add `data-sort-order="{sort}"` to the results section element** (`id="report-results"`).

7. **Write Playwright assertions verifying:**
   - With `sort=events_asc`: the first result card has the lowest event count (legacy-import, events=4).
   - With `sort=name_asc`: the first result card is alphabetically first by `report_id` (api-latency).
   - The sort dropdown `data-sort-order` attribute reflects the current sort after an HTMX
     partial swap triggered by a facet filter change.
   - Facet counts are identical regardless of sort value (sort never affects counts).

## Outputs

- Updated query state model (new `sort` field).
- `sort_rows` helper function.
- Sort select element in the rendered HTML with all required data-* attributes.
- Updated fingerprint string including `sort`.
- Playwright tests for sort correctness and persistence.

## Related doctrine

- `context/doctrine/search-sort-scroll-layout.md`

## Common pitfalls

- **Applying sort to counts.** Sort must never be passed into `facet_counts` or
  `exclude_impact_counts`. It only affects the result row order.
- **Resetting the sort dropdown to the default on every HTMX swap.** The results fragment
  must pre-select the current sort value in the `<option selected>` attribute.
- **Treating `sort` as a multi-value parameter.** It is always a single string value.
- **Not using a stable sort.** When `events` values are equal, use `report_id` as a
  tiebreaker to ensure consistent ordering across renders.

## Stop conditions

- With `sort=events_asc`, the first rendered result card is `legacy-import` (events: 4).
- With `sort=name_asc`, the first rendered result card is `api-latency` (alphabetically first).
- The sort dropdown retains its selected value after an HTMX partial swap triggered by a
  facet filter checkbox change.
- Facet option counts are identical between `sort=events_asc` and `sort=events_desc`
  for the same filter state.
