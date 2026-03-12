# CLAUDE.md

Purpose: route Claude-style assistants to the minimum useful context while keeping routing deterministic.

This file should stay short. It delegates doctrine, workflows, stacks, archetypes, and examples to scoped files.

## Required First Reads

Read these first:

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `context/router/load-order.md`
4. `context/router/task-router.md`

Read `context/router/stack-router.md` and `context/router/archetype-router.md` only when the stack or archetype is not already clear from the manifest and repo signals.

## Routing Policy

Use this sequence:

1. Identify the task from the operator's normal English request.
2. Identify the archetype.
3. Identify the active stack.
4. Load only the doctrine docs needed for that task.
5. Load one workflow.
6. Load one archetype pack.
7. Load only the stack packs that match the active change surface.
8. Load the preferred canonical example for the pattern.

Do not recursively read the repository just because context is available.

## Shared Truth Layer

Treat these as durable truth:

- `manifests/repo.profile.yaml`
- `context/doctrine/`
- router rules in `context/router/`

Treat workflows, archetypes, stacks, examples, and templates as selected support context, not always-on truth.

## Example-First Policy

- Prefer one canonical example per pattern family.
- Use secondary examples only when the preferred example is incompatible with the active stack.
- If no suitable example exists, say so explicitly before generating a new pattern.

## When To Stop

Stop and surface the problem when:

- repo signals and manifest metadata conflict
- the task spans multiple archetypes without an explicit composition rule
- the task touches persistence, queues, search indexes, or cross-service boundaries but lacks a real Docker-backed integration-test path
- Docker-backed changes would blur dev and test isolation
- only deprecated or contradictory examples exist

## Model-Specific Note

Claude can absorb longer prose, but this repo is tuned for smaller composable bundles. Follow the router and avoid loading neighboring files unless the task requires them.

## Delegated Files

- `docs/agent-context-architecture.md`
- `context/router/task-router.md`
- `context/router/stack-router.md`
- `context/router/archetype-router.md`
- `context/router/alias-catalog.md`
- `context/router/example-priority.md`
- `context/router/stop-conditions.md`
