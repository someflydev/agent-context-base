# Decide When To Create Project Docs Dir

Use this workflow when a derived repo is considering a root-level `docs/` directory.

## Goal

Create `docs/` only when the repo has multiple stable topics that no longer fit cleanly in a small root README or generated profile.

## Sequence

1. list the documentation topics that already have implemented backing
2. remove topics that are still speculative, diagram-only, or roadmap-like
3. confirm the remaining topics are distinct enough to justify separate files
4. check whether the repo owner is ready to maintain those files as implementation changes
5. decide whether to:
   - defer `docs/`
   - create one narrowly scoped operational doc
   - create a small `docs/` directory with only proven topics

## Good Reasons To Create `docs/`

- there are several stable operating topics such as deployment, event contracts, or storage notes
- one implementation milestone now spans enough surfaces that the README would become noisy
- diagrams can now describe committed architecture rather than guesses

## Bad Reasons To Create `docs/`

- the repo feels too empty
- a generator usually makes a docs directory
- the team wants architecture diagrams before the architecture exists
- the content would mostly restate plans and aspirations

## Output Rule

If `docs/` is created, start small and keep every file tied to an implemented boundary.

## Related Doctrine

- `context/doctrine/documentation-timing-discipline.md`
- `context/doctrine/mermaid-diagram-freshness.md`
