# CLAUDE.md

Use this file as the assistant boot entrypoint, not as the full source of truth.

Follow `docs/context-boot-sequence.md` before loading deeper context.

## First Reads

1. `README.md`
2. `docs/context-boot-sequence.md`
3. `docs/repo-purpose.md`
4. `docs/repo-layout.md`
5. `docs/session-start.md`
6. `context/router/task-router.md`

After those reads and a narrow repo-signal check, read `MEMORY.md` if it exists.

## Minimal Context Policy

Prefer this order:

1. router
2. anchor
3. doctrine
4. workflow
5. archetype
6. stack
7. canonical example
8. template only if scaffolding is required

Load one dominant path, not a broad survey.

## Running Verifications

Verification scripts use `unittest`, not pytest. Run them with:

```
python3.14 -m unittest verification.examples.data.test_storage_examples -v
```

Use dotted module paths from the repo root. Never invoke `pytest`.

## Guardrails

- Infer intent from normal language and repo signals.
- Prefer manifests and canonical examples over improvisation.
- Treat templates as starter scaffolds, not authoritative patterns.
- During new-project classification, make storage and broker choices explicit instead of silently accepting generic defaults.
- If the prompt implies persistence, queues, search, or eventing but leaves the backing systems unstated, ask the operator to confirm the intended storage/broker set before generation.
- Preserve the operator's initial prompt in the generated repo and use it to justify storage suggestions.
- When running inside `agent-context-base`, assume the task is to generate a new repo unless the operator explicitly says the base repo itself should be changed.
- Use `MEMORY.md` only as continuity state.
- Keep `docker-compose.yml` and `docker-compose.test.yml` distinct and isolated.
- Stop when stack choice, archetype choice, or verification posture is still ambiguous.

For deeper operating rules, see `docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`.
