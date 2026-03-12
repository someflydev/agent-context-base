# Refactor

Use this workflow when structure should improve without changing intended behavior.

## Preconditions

- the current behavior is understood well enough to preserve
- existing tests are present or can be added first

## Sequence

1. define the exact behavior that must stay unchanged
2. add missing safety tests if coverage is thin
3. simplify one change surface at a time
4. keep naming and file boundaries clear
5. rerun smoke tests and any relevant integration tests
6. update docs only if the public shape changed

## Outputs

- simpler code or docs
- unchanged behavior
- strengthened safety tests where needed

## Related Docs

- `context/doctrine/naming-and-clarity.md`
- `context/doctrine/commit-hygiene.md`

## Common Pitfalls

- changing behavior during structural cleanup
- doing a repo-wide rewrite with weak test coverage
- folding unrelated cleanup into the same commit

