# Documentation Timing Discipline

This doctrine exists because derived repos often get a polished root `README.md`, a broad `docs/` tree, and architecture diagrams before the implementation is real enough to support them. That usually creates four avoidable failures:

- premature READMEs that describe intent instead of implemented behavior
- speculative docs that harden guesses into apparent facts
- Mermaid diagrams that drift after the first structural change
- derived repos that document imagined architecture instead of committed reality

Delaying front-facing documentation improves trust because the docs are then written against code, tests, routes, storage boundaries, and operating behavior that already exist. The result is usually shorter, clearer, and easier to keep current.

## Core Rule

Do not create a substantial root `README.md` or a root-level `docs/` directory in a new derived repo until the implementation has earned them.

## What Counts As "Earned"

The repo usually has enough substance when most of these are true:

- at least one meaningful end-to-end implementation slice exists
- the primary entrypoints and storage boundaries are committed, not hypothetical
- basic verification already proves the main path
- the likely repo shape is visible from real files, not only intentions
- the maintainer is ready to treat docs and diagrams as first-class artifacts

## Practical Exceptions

Minimal scaffolding is still acceptable when it stays honest and narrowly useful:

- `AGENT.md`, `CLAUDE.md`, manifests, and generated profiles that help assistants start
- a narrowly scoped operational note created because a user explicitly asked for it
- a concise placeholder only when it clearly says the public-facing repo docs are intentionally deferred

The exception is not permission to generate a speculative README with future-tense architecture prose.

## Writing Order

Prefer this order in a new derived repo:

1. implement the first real slice
2. add verification for the changed boundary
3. observe the stable repo shape
4. create the root `README.md` only when it can describe the actual system honestly
5. create `docs/` only when there are multiple stable topics worth separating

## Maintenance Rule

Once the root `README.md`, `docs/`, or Mermaid diagrams exist, they stop being optional decoration. They must be updated whenever implementation changes make them misleading.

## Related Doctrine

- `context/doctrine/README-gating-for-derived-repos.md`
- `context/doctrine/mermaid-diagram-freshness.md`
- `context/doctrine/core-principles.md`
