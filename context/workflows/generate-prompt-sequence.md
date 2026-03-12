# Generate Prompt Sequence

Use this workflow when a task should be split into explicit prompt files or prompt steps.

## Preconditions

- the work benefits from staged execution
- the sequence can be expressed as monotonic steps

## Sequence

1. identify the end state
2. break work into commit-friendly increments
3. assign strictly monotonic prompt numbers
4. reference exact filenames in each prompt
5. make each prompt depend on actual repo state, not wishful state
6. keep each prompt dominated by one main goal

## Outputs

- an ordered prompt sequence with explicit filenames
- a clear mapping from prompts to expected commits or change sets

## Related Docs

- `context/doctrine/prompt-first-conventions.md`
- `context/doctrine/commit-hygiene.md`

## Common Pitfalls

- renumbering older prompts
- making one prompt depend on files not yet created
- vague instructions like "update the API stuff"

