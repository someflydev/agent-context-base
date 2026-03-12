# Post-Flight Refinement

Use this workflow after implementation to tighten quality without reopening architecture debates.

## Preconditions

- the main implementation path already works

## Sequence

1. remove obvious naming drift
2. confirm references and docs are accurate
3. tighten comments and examples
4. rerun validations and tests
5. split the work into reviewable commits if needed

## Outputs

- clearer naming
- cleaner docs
- smaller review surface

## Related Docs

- `context/doctrine/naming-and-clarity.md`
- `context/doctrine/commit-hygiene.md`

## Common Pitfalls

- turning refinement into endless redesign
- adding unrelated features while "cleaning up"
- forgetting to update manifests after moving files

