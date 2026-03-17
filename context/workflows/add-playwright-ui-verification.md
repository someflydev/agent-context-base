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

## Critical User Journey Tests

Isolated feature tests (playwright-split-filter-panel-example.spec.ts,
playwright-search-sort-example.spec.ts) verify individual rendering rules in
isolation — one rule per test, one URL per test. They are the right tool for
confirming that RULE 1, RULE 2, RULE 3, sort, and scroll attributes are rendered
correctly under specific URL params.

CUJ tests (playwright-cuj-filter-example.spec.ts) test the same features as a
user actually uses them: in sequence, in combination, and with state carried
across multiple steps. Each CUJ corresponds to a named scenario with a clear
user goal, a sequence of actions, and assertions at each step and at the end.

Key distinctions:

- CUJ tests use a **page object model** (`ReportsFilterPage`) to avoid repeating
  DOM selectors across 10 test scenarios. Each helper method returns a typed value
  or sensible null/undefined.
- CUJ tests exercise compound filter states (include + exclude + search + sort
  simultaneously) that isolated tests cannot cover without combining them.
- CUJ tests include scroll independence (CUJ-9: programmatic scroll + HTMX swap)
  and URL round-trip (CUJ-10: bookmark → reload → identical view).
- CUJ tests use URL navigation for most state transitions; HTMX interaction is
  used only where the test specifically targets partial-swap behaviour (CUJ-7, CUJ-9).

Canonical CUJ test example:
`examples/canonical-integration-tests/playwright-cuj-filter-example.spec.ts`

## Stop Conditions

- the spec proves one meaningful backend-driven flow end to end
- assertions read like semantics, not browser choreography
