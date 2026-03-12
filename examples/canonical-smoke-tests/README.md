# Canonical Smoke Test Examples

Use this category for preferred happy-path verification patterns.

Primary file in this category:

- `fastapi-smoke-test-example.py`

## A Strong Canonical Smoke Example Should Show

- deterministic setup
- a small number of assertions
- clear failure output
- one primary boot or happy-path check
- how smoke tests pair with deeper integration tests when boundaries matter

## Choosing This Example

Choose this category when the main question is "what is the smallest meaningful confidence check?"

## Drift To Avoid

- examples that become full end-to-end suites
- mocks that hide the wiring the smoke test is meant to prove
- examples that ignore the need for real-infra integration tests for meaningful boundaries
