# CLAUDE.md

Purpose: route Claude-style assistants to the minimum useful context without turning this file into a doctrine dump.

## Required First Reads

Load these files first:

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `context/router/load-order.md`
4. `context/router/task-routing.md`

## Routing Policy

Use a layered context strategy:

1. Durable doctrine first.
2. Then one workflow for the task.
3. Then one archetype pack.
4. Then only the stack packs actually needed.
5. Then canonical examples relevant to the exact change surface.

Do not recursively read the whole repository to "get context."

## Shared Doctrine

Treat the following as the durable truth layer:

- `context/doctrine/`
- infrastructure invariants declared in `manifests/repo.profile.yaml`

Treat workflows, stack packs, archetype packs, and examples as delegated context selected per task.

## Example-First Policy

- Check canonical examples before generating a new implementation pattern.
- Prefer examples labeled preferred in the example index or manifest.
- Avoid blending multiple examples that solve the same problem in incompatible ways.

## When To Stop

Pause and surface the uncertainty if:

- the task spans more than one archetype and there is no explicit composition rule
- repo signals disagree with the manifest profile
- a significant infra or persistence change has no smoke-test or minimal integration-test path
- only deprecated examples exist for the requested change

## Model-Specific Note

Claude often tolerates longer prose, but this repo is optimized for smaller deterministic bundles. Follow the router files instead of expanding the context window unnecessarily.

## Delegated Files

- `context/router/load-order.md`
- `context/router/task-routing.md`
- `context/router/example-priority.md`
- `context/router/stop-conditions.md`
- `docs/agent-context-architecture.md`
