# Add Playwright UI Verification

## Purpose

Add Playwright coverage for backend-driven interfaces where query correctness matters.

## When To Use It

- HTMX fragments are part of the user contract
- backend-generated counts or charts must stay aligned with filters
- DOM-only assertions would miss semantic drift

## Sequence

1. identify the smallest backend-driven user flow worth proving
2. add stable selectors or `data-*` markers if the UI lacks them
3. write assertions for visible rows, result count, and one chart or count payload
4. avoid screenshot-only checks unless they support a semantic assertion
5. keep the spec focused on one or two meaningful flows

## Outputs

- Playwright spec
- documented selectors or state markers used by the spec
- proof that backend-driven UI state is semantically correct

## Related Doctrine

- `context/doctrine/playwright-verification-philosophy.md`
- `context/doctrine/backend-driven-ui-correctness.md`

## Common Pitfalls

- verifying only click success or DOM presence
- brittle selectors tied to styling instead of semantics
- not checking chart or filter-count payloads

## Stop Conditions

- the spec proves one meaningful backend-driven flow end to end
- assertions read like semantics, not browser choreography
