# Add Dynamic Counts

## Purpose

Add accurate result counts and per-option filter counts to a backend-driven interface.

## When To Use It

- a faceted filter UI needs counts next to options
- users need confidence that filters reflect live query results

## Sequence

1. define the result-count query semantics
2. define the per-facet count semantics for each dimension
3. implement count generation in the same backend boundary as the result query
4. render counts in a fragment or payload with stable markers
5. verify counts against deterministic backend fixtures

## Outputs

- result-count computation
- option-count computation
- count fragment or JSON payload
- verification of representative count cases

## Related Doctrine

- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/backend-driven-ui-correctness.md`

## Common Pitfalls

- cached or stale counts reused after filter changes
- same-dimension include logic not documented
- counts rendered without the corresponding state markers

## Stop Conditions

- visible result count is exact
- representative option counts are exact under active include/exclude filters
