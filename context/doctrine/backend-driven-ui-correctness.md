# Backend-Driven UI Correctness

Backend-driven UI work matters when the backend is the source of truth for both data semantics and interactive state.

## Why This Matters

HTMX, Tailwind, and Plotly can produce fast, maintainable interfaces, but only if the backend owns the query contract. If result counts, filter counts, fragments, and chart payloads are computed by different logic paths, the UI can look responsive while being wrong.

## Core Rules

- one query-state model must drive result rows, result counts, facet counts, and chart payloads
- backend-generated fragments are part of the contract, not disposable view text
- Tailwind classes should improve readability, not hide missing state markers or ambiguous selectors
- HTMX responses should expose real backend state with stable ids, `data-*` markers, and explicit fragment boundaries
- Plotly payloads must be derived from the same filtered dataset as the visible results

## Correctness Surface

Treat these as one change surface:

- request query parsing
- include and exclude filter semantics
- result query
- total result count
- per-option facet counts
- fragment rendering
- chart-data endpoint

If any one of those changes, review the others.

## Preferred Pattern

1. normalize query state into one explicit backend structure
2. run one named query path for visible rows
3. derive counts and chart payloads from the same normalized state
4. render fragments that echo result count, active filters, and query fingerprint
5. verify semantics with focused backend tests and Playwright assertions

## Failure Modes

- computing counts from a looser query than the result set
- mixing include and exclude semantics implicitly in template code
- returning fragments that do not expose the state they represent
- letting chart endpoints drift from the result query
- writing UI tests that only prove clicks occurred
