# Terminal Smoke Baseline

## Purpose

Verifies that all terminal canonical examples pass their CLI smoke tests in
non-interactive, fixture-backed mode.

## Applies To

All examples in `examples/canonical-terminal/`

## Preconditions

- `examples/canonical-terminal/fixtures/jobs.json` exists
- each example's dependencies are installed

## Test Sequence

For each implemented language example:

1. Run the CLI smoke test in headless mode.
2. Assert exit code `0`.
3. Assert at least one marker or JSON field in output.

## Pass Criteria

- all CLI smoke tests exit `0`
- output contains expected markers or JSON structure
- no network calls are made during the smoke run

## Failure Modes

- missing fixture file: precondition failure, not a smoke-test failure
- non-zero exit code: implementation error
- missing marker or JSON field: output assertion contract violated
