# Add Faceted Filter UI

## Purpose

Add a backend-driven faceted filtering surface where results, fragments, and counts stay aligned.

## When To Use It

- adding an HTMX filter sidebar or toolbar
- introducing server-rendered result fragments
- exposing counts next to filter options

## Sequence

1. define the normalized query-state model
2. implement the filtered result query and total result count together
3. render a result fragment with stable ids and backend state markers
4. add facet-count generation for the visible filter dimensions
5. add focused verification for query semantics and fragment output

## Outputs

- query-state parser
- result fragment endpoint
- filter-panel fragment or equivalent
- verification for counts and visible rows

## Related Doctrine

- `context/doctrine/backend-driven-ui-correctness.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/filter-state-and-query-state.md`

## Common Pitfalls

- computing counts from different query semantics than the result list
- hiding state inside template-only logic
- omitting stable fragment markers needed by HTMX and tests

## Stop Conditions

- result count and visible rows match the active query state
- at least one representative facet shows verified counts

## Standard Enhancements

After the base filter UI is working and verified, apply these three enhancements as the
canonical next step:

1. **Text search bar** — a free-text input that narrows results and counts on top of
   active facet filters. Follow `context/workflows/add-text-search-to-filter-ui.md`.

2. **Sort order dropdown** — a select element in the results section header that controls
   result ordering without affecting any counts. Follow
   `context/workflows/add-sort-order-to-results.md`.

3. **Independent scroll layout** — the filter panel and results section sit side-by-side
   and each scrolls independently. Follow RULE 6 in
   `context/doctrine/search-sort-scroll-layout.md`.

These three features are applied together in the reference implementation:
`examples/canonical-api/fastapi-search-sort-filter-example.py`.
