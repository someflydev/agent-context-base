# AGENT.md

Purpose: route Codex-style agents to the smallest relevant context bundle.

## First Reads

Always load these first and in this order:

1. `README.md`
2. `manifests/repo.profile.yaml`
3. `context/router/load-order.md`
4. `context/router/task-routing.md`

## Load Smallest Relevant Bundle

After the first reads:

1. Infer the archetype from the repo profile and task wording.
2. Infer the active stack from repo signals and the profile.
3. Load only the doctrine files required by the task.
4. Load one workflow file that matches the task.
5. Load one archetype pack and only the necessary stack packs.
6. Load canonical examples before inventing a new pattern.

Do not bulk-load `context/`, `examples/`, or `docs/`.

## Context Priority

Use this order when sources conflict:

1. Current repo code and tests
2. `manifests/repo.profile.yaml`
3. doctrine files
4. workflow files
5. stack/archetype packs
6. canonical examples
7. templates

## Canonical Example Rule

- Prefer an existing canonical example over synthesizing a new pattern.
- If multiple examples conflict, use the one marked `preferred: true` in its index metadata.
- If no suitable example exists, say that explicitly before introducing a new pattern.

## Do Not Load Unless Needed

Avoid loading unrelated stacks, retired examples, or archetypes that are not active in the repo.

Common skip cases:

- do not load `context/stacks/elixir-phoenix.md` for a FastAPI task
- do not load storage packs for a pure prompt-sequence edit
- do not load deploy docs for a local-only refactor unless deployment behavior is touched

## Stop Conditions

Stop and ask for clarification, or state the gap clearly, if:

- the repo profile is missing or stale
- the archetype cannot be inferred with confidence
- multiple canonical examples conflict and none is preferred
- the task touches persistence, queues, search, or cross-service boundaries but no real integration path is defined
- the task requires changing Docker-backed infra and the dev/test isolation rules are unclear

## Guardrails

- Do not invent stack conventions when a stack pack exists.
- Do not invent port numbers ad hoc; use the repo profile and infra conventions.
- Do not seed or reset test data against dev-like stores.
- Do not treat `AGENT.md` as the full instruction set; it is only the router.

## Key Delegates

- Load order: `context/router/load-order.md`
- Task routing: `context/router/task-routing.md`
- Example priority: `context/router/example-priority.md`
- Stop conditions: `context/router/stop-conditions.md`
- Architecture reference: `docs/agent-context-architecture.md`
