# AGENT.md

Purpose: boot the assistant into the smallest useful context bundle for this repo.

Use `docs/context-boot-sequence.md` as the startup contract. Durable rules live under `context/doctrine/`.

## First Reads

1. `README.md`
2. `docs/context-boot-sequence.md`
3. `docs/repo-purpose.md`
4. `docs/repo-layout.md`
5. `docs/session-start.md`
6. `context/router/task-router.md`

After those reads and a narrow repo-signal check, read `MEMORY.md` if it exists. Load stack and archetype routers only when the task still needs narrowing.

## Bundle Discipline

Default first-pass bundle:

1. one router
2. one anchor if helpful
3. only the doctrine files the task activates
4. one workflow
5. one archetype if repo shape matters
6. only the active stack packs
7. one canonical example

Do not bulk-load `context/`, `examples/`, `templates/`, or `manifests/`.

## Operating Rules

- Infer intent from normal language, not internal filenames.
- Prefer manifest-defined bundles over improvised loading.
- Treat templates as scaffolds and examples as the preferred pattern source.
- Use `MEMORY.md` only for continuity, never as doctrine.
- Update `MEMORY.md` at meaningful stop points and create a handoff snapshot when a later session is likely.

## Stop When

- more than one workflow, stack, or archetype still looks primary
- storage, queue, search, deployment, or Compose isolation changes lack a minimal verification path
- prompt numbering or generated-profile references would become ambiguous
- the next step would require loading broad adjacent context "just in case"

For deeper runtime behavior, see `docs/usage/ASSISTANT_BEHAVIOR_SPEC.md` and `context/doctrine/stop-conditions.md`.
