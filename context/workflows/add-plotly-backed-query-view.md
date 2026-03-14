# Add Plotly-Backed Query View

## Purpose

Add a Plotly chart whose payload stays synchronized with backend query state and visible results.

## When To Use It

- filtered results also need a chart or trend view
- chart consumers must trust the same backend query semantics as the table or cards

## Sequence

1. reuse the normalized query-state model from the result view
2. implement chart aggregation from the same filtered dataset
3. include result count, active filters, or query fingerprint in the chart payload
4. wire the page or fragment to fetch chart data from the backend
5. verify chart payload alignment with representative filter states

## Outputs

- chart-data endpoint
- page or fragment wiring for Plotly consumers
- verification of chart and result alignment

## Related Doctrine

- `context/doctrine/backend-driven-ui-correctness.md`
- `context/doctrine/filter-state-and-query-state.md`

## Common Pitfalls

- chart endpoint silently dropping some active filters
- chart totals derived from a different query window than the visible rows
- no response markers tying the chart payload back to query state

## Stop Conditions

- chart payload and visible result state agree for representative filters
- the chart endpoint exposes enough state for verification
