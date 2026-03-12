# AGENT.md

Purpose: route Codex-style agents to the smallest useful context bundle for the current task.

This file is a router, not a doctrine dump.

## Required First Reads

Read these in order:

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `context/router/load-order.md`
4. `context/router/task-router.md`

Read `context/router/stack-router.md` and `context/router/archetype-router.md` only if the task, repo signals, or manifest do not already make the stack and archetype obvious.

## Routing Rules

1. Infer the task from normal English, not from internal file names.
2. Infer the repo archetype from `manifests/repo.profile.yaml`, repo structure, and task wording.
3. Infer the active stack from manifest metadata, lockfiles, tool files, source trees, and existing canonical examples.
4. Load only the doctrine docs required by the exact change.
5. Load one workflow first. Load a second workflow only if the task clearly spans both.
6. Load one primary archetype pack. Load a second archetype only if the repo is intentionally composite.
7. Load only the stack packs that match the active code path.
8. Consult preferred canonical examples before introducing a new pattern.
9. Open templates only for bootstrap or scaffold tasks.

Do not bulk-load `context/`, `examples/`, `templates/`, or `docs/`.

## Context Priority

When sources disagree, prefer:

1. current repo code, tests, and configuration
2. `manifests/repo.profile.yaml`
3. doctrine docs
4. workflow docs
5. archetype docs
6. stack docs
7. canonical examples
8. templates

## Minimal Bundle Rule

Load the smallest relevant bundle first:

- repo profile
- router docs
- task-specific doctrine
- one workflow
- one archetype
- required stack packs
- preferred example

Escalate only when the active change surface is still ambiguous.

## Canonical Example Rule

- Prefer one preferred example for a pattern family.
- Do not blend multiple conflicting examples into a hybrid pattern.
- If no suitable example exists, say so explicitly and create the smallest new pattern consistent with doctrine and stack docs.

## Stop Conditions

Stop and surface the gap when:

- manifest signals and repo contents disagree
- more than one archetype looks primary and there is no composition rule
- more than one stack looks active for the target surface
- the change touches persistence, queues, search, or cross-service boundaries and no minimal real-infra integration-test path is defined
- the change touches Docker-backed infra and dev/test isolation is unclear
- the only matching example is retired or contradictory

## Guardrails

- Do not invent stack conventions when a stack pack exists.
- Do not invent ports ad hoc; follow the manifest port bands.
- Keep Compose filenames conventional: `docker-compose.yml` and `docker-compose.test.yml`.
- Use repo-derived Compose `name:` values so dev and test stacks can run in parallel.
- Never let test seeds, fixtures, env files, databases, or volumes touch dev-like data.
- Treat `AGENT.md` as a router only. The durable truth lives in doctrine and manifests.

## Key Delegates

- `docs/agent-context-architecture.md`
- `context/router/task-router.md`
- `context/router/stack-router.md`
- `context/router/archetype-router.md`
- `context/router/alias-catalog.md`
- `context/router/example-priority.md`
- `context/router/stop-conditions.md`
