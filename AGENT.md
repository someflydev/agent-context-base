# AGENT.md

Purpose: route the assistant to the smallest relevant context bundle for the current task.

This file is a router. Durable doctrine lives under `context/doctrine/`.
Follow `docs/context-boot-sequence.md` as the deterministic startup contract for this repo.

## Required First Reads

Read these first:

1. `README.md`
2. `docs/context-boot-sequence.md`
3. `docs/repo-purpose.md`
4. `docs/repo-layout.md`
5. `docs/session-start.md`
6. `context/router/task-router.md`

Only then load `context/router/stack-router.md`, `context/router/archetype-router.md`, or a manifest if the task still needs narrowing.

## Smallest Relevant Bundle

Default bundle:

1. one task router file
2. one anchor if a compact reminder helps
3. only the doctrine files needed for the change
4. one primary workflow
5. one archetype if project shape matters
6. the stack files that match the touched surface
7. one preferred canonical example

Do not bulk-load `context/`, `examples/`, `templates/`, or `manifests/`.

## Task Inference

Infer the task from ordinary language. Do not require the user to know internal filenames.

- "add an endpoint" -> `context/workflows/add-api-endpoint.md`
- "bootstrap a repo" -> `context/workflows/bootstrap-repo.md`
- "fix a bug" -> `context/workflows/fix-bug.md`
- "add smoke tests" -> `context/workflows/add-smoke-tests.md`
- "set up local rag" -> `context/workflows/add-local-rag-indexing.md`

Use repo signals, manifests, and touched files to infer stack and archetype.

## When To Load More

Load doctrine when the task affects naming, testing, prompt-first rules, commit shape, Docker isolation, deployment, or example selection.

Load workflows when the task is action-oriented.

Load stacks when implementation details depend on a concrete language, framework, storage system, queue, or search engine.

Load archetypes when the project shape matters more than a single framework choice.

Load examples only after the active workflow and stack are known.

## Canonical Example Priority

Prefer one canonical example over blending several near-matches. If no example fits, state that and follow doctrine plus stack guidance.

## Stop Conditions

Use `context/doctrine/stop-conditions.md` as the explicit pause-point reference.

Stop and surface the gap if:

- the task implies more than one primary archetype and composition is unclear
- more than one stack is plausible for the touched surface
- persistence, messaging, search, or deployment behavior changed but no minimal verification path is defined
- Docker dev and test isolation is unclear
- prompt numbering or profile references would stop being monotonic or explicit
- the request would cause context sprawl instead of a focused bundle

## Anti-Sprawl Rules

- Do not turn `AGENT.md` into a doctrine dump.
- Do not invent new router names when an existing workflow or stack clearly fits.
- Do not load multiple examples unless comparing and resolving a conflict.
- Do not promote templates to canonical examples.
