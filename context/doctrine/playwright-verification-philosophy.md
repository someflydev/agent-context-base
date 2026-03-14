# Playwright Verification Philosophy

Use Playwright to verify backend-driven UI semantics, not to simulate busywork.

## What To Prove

For HTMX-style interfaces, Playwright should confirm:

- the right rows appear after a filter change
- the visible result count matches the filtered dataset
- counts next to filter options match backend semantics
- backend-generated fragments expose stable state markers
- chart payloads stay aligned with the same filter state

## What Not To Center

- animation timing
- pixel-perfect styling checks
- long click scripts without semantic assertions
- screenshots as the only proof of correctness

## Preferred Assertions

- exact count text or `data-result-count`
- exact option counts for a few representative facets
- exact active filter chips or hidden-input state
- exact chart payload fields fetched from the backend
- exact fragment ids, `hx-swap-oob`, or query fingerprint markers when they are part of the contract

## Layering

Playwright complements backend tests. It does not replace query-level verification.

Use backend tests for:

- filter parser logic
- count semantics
- chart aggregation

Use Playwright for:

- state propagation through the page
- fragment replacement behavior
- end-to-end semantic alignment

## Stop Conditions

Stop when Playwright only proves that a request happened. The test is not done until it proves that the backend-driven UI reflects the intended query semantics.
