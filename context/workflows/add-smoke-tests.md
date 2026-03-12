# Add Smoke Tests

Use this workflow when a repo or feature needs fast confidence checks for the main path.

## Preconditions

- the primary path to prove is known
- the boot command or entrypoint is known

## Sequence

1. choose the smallest meaningful happy path
2. define deterministic setup and teardown
3. write a fast smoke test with few assertions
4. verify it fails loudly on obvious breakage
5. identify whether the feature also needs minimal real-infra integration tests

## Outputs

- one or more fast smoke tests
- documented invocation path if needed

## Related Docs

- `context/doctrine/smoke-test-philosophy.md`
- `smoke-tests/README.md`

## Common Pitfalls

- turning smoke tests into a slow integration suite
- using mocks to prove wiring that should be exercised for real
- assuming smoke tests are enough for storage-backed behavior

