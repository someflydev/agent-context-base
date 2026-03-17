# Context Bundle Assembly

Use this skill to assemble the minimal justified context bundle for the current task.

## Procedure

1. identify the active change surface — what the task directly touches
2. mark each candidate context item as required or optional:
   - **required**: the change surface directly touches it (a storage write requires the storage stack doc; a route change requires the stack's API surface doc)
   - **optional**: nearby but not on the change surface (the Postgres doc is not required for a pure data-transform function)
3. apply load-order discipline:
   - doctrine before workflow (invariants before steps)
   - workflow before stack (what to do before how to do it)
   - stack before example (framework rules before implementation patterns)
   - one example over several near-matches
4. one-dominant-path rule: load one workflow, one stack surface, one archetype — if two workflows look equally relevant, pick the one that touches the change surface most directly
5. second item allowed only when the task has a clear orthogonal concern (e.g., a storage write plus a smoke test) — two clearly distinct surfaces can each load one item
6. stop and raise ambiguity if the dominant path is still unclear after steps 1–5

## Good Triggers

- "what context do I need for this task"
- "what should I load"
- "required vs optional context"
- "how to assemble the context bundle"
- "I'm not sure what to load"

## Avoid

- loading several near-match examples as a hedge
- loading doctrine "just in case" without a clear trigger
- widening the bundle when routing is still ambiguous — stop instead
- loading the full context directory when the task has one clear surface
