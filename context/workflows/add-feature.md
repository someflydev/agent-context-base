# Add Feature

Use this workflow when the task is to add a meaningful user-facing or operator-facing capability.

## Preconditions

- the target archetype is known or inferable
- the primary stack for the touched surface is known
- relevant doctrine for naming and testing has been loaded

## Sequence

1. restate the feature in one sentence
2. identify the touched files and boundaries
3. load the primary stack doc and one matching example
4. implement the smallest useful version
5. add or update smoke tests
6. add minimal real-infra integration tests if persistence, queueing, search, or service boundaries changed
7. refine names, docs, and commit shape

## Outputs

- working implementation
- focused tests
- any needed docs or manifest updates

## Related Docs

- `context/doctrine/testing-philosophy.md`
- `context/doctrine/canonical-examples.md`
- `context/workflows/post-flight-refinement.md`

## Common Pitfalls

- adding abstractions before the first working path exists
- skipping integration tests for a database-backed feature
- blending patterns from multiple examples

