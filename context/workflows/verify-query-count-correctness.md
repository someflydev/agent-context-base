# Verify Query Count Correctness

## Purpose

Prove that result counts, option counts, and chart payloads reflect the real backend query semantics.

## When To Use It

- faceted filtering changed
- include or exclude semantics changed
- counts or charts are suspected to be wrong

## Sequence

1. fix the intended query-state semantics in one deterministic fixture set
2. verify filtered rows and total result count together
3. verify representative per-facet option counts
4. verify chart payload alignment with the same filter state
5. add or update Playwright assertions if the UI exposes the behavior

## Outputs

- deterministic count-verification cases
- documented count semantics
- updated backend or Playwright checks when drift is found

## Related Doctrine

- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/filter-state-and-query-state.md`
- `context/doctrine/playwright-verification-philosophy.md`

## Common Pitfalls

- asserting counts without proving the underlying rows
- only testing the unfiltered case
- skipping chart verification even though the page displays a chart

## Stop Conditions

- representative filtered cases match exact expected counts
- chart and fragment state match the verified query state
