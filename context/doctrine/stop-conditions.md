# Stop Conditions

Stop expanding or implementing when one of these conditions is true:

- more than one primary archetype fits and the composition rule is still unclear
- more than one stack is plausible for the touched surface
- a storage, queue, search, or deployment boundary changed but no minimal verification path exists
- Compose naming, host-port allocation, or dev-vs-test isolation is ambiguous
- prompt numbering, profile references, or generated file names would stop being monotonic or explicit
- context expansion would load several examples or stacks "just in case"

## Response Rule

When a stop condition triggers:

1. name the ambiguity directly
2. identify the smallest missing decision or missing verification path
3. avoid inventing a blended pattern to keep momentum

## Related Files

- `context/doctrine/context-loading-rules.md`
- `context/doctrine/compose-port-and-data-isolation.md`
- `context/doctrine/prompt-first-conventions.md`
- `docs/session-start.md`
