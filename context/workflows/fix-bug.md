# Fix Bug

Use this workflow when behavior is wrong, unstable, or inconsistent with an existing contract.

## Preconditions

- the failing behavior is described clearly enough to reproduce or reason about
- the affected stack is known

## Sequence

1. capture the actual bug in one sentence
2. localize the failing boundary or code path
3. add or tighten a test that proves the bug
4. implement the narrowest fix that restores the contract
5. add smoke coverage if the bug affects a primary path
6. add real-infra integration coverage if the bug involved storage, queues, search, or service boundaries
7. confirm no nearby behavior regressed

## Outputs

- bug fix
- regression test
- any needed docs or example updates

## Related Docs

- `context/doctrine/testing-philosophy.md`
- `context/workflows/post-flight-refinement.md`

## Common Pitfalls

- patching symptoms without finding the boundary that failed
- fixing behavior but leaving no regression test
- broad refactors disguised as bug fixes

