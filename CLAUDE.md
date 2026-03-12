# CLAUDE.md

Use this file as a routing entrypoint, not as the full source of truth.

Start with:

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `docs/session-start.md`
5. `context/router/task-router.md`

Then infer the smallest useful bundle instead of loading the whole repo.

## Routing Discipline

- Infer intent from normal language.
- Infer stack from repo signals, manifest names, and the files being changed.
- Infer archetype from the project goal, deployment posture, and dominant change surface.
- Load doctrine first when the task can drift into naming, testing, prompts, deployment, or context bloat.
- Load a single workflow before mixing several task playbooks.
- Load one preferred example before inventing a new pattern.

## Practical Heuristics

If the user says:

- "add endpoint", "new route", "new handler" -> read `context/workflows/add-api-endpoint.md`
- "ship", "deploy", "dokku", "Procfile" -> read `context/workflows/add-deployment-support.md`
- "seed", "fixtures", "starter data" -> read `context/workflows/add-seed-data.md`
- "smoke test", "health check", "happy path" -> read `context/workflows/add-smoke-tests.md`
- "bootstrap", "new repo", "foundation" -> read `context/workflows/bootstrap-repo.md`

Then add only the stack and archetype files the task truly needs.

## Minimal Context Policy

Prefer this order:

1. router
2. anchor
3. doctrine
4. workflow
5. archetype
6. stack
7. canonical example
8. template

Templates are scaffolds. Examples are preferred patterns. Keep them distinct.

## When To Pause

Pause and explain the ambiguity when:

- stack choice is unclear from the task and repo signals
- a persistence or service-boundary change lacks real-infra test guidance
- deployment, Compose isolation, or prompt numbering would become ambiguous
- prompt numbering or referenced filenames would become non-monotonic or vague
- a request would create an oversized context bundle with no clear primary path

## Guardrails

- Keep `CLAUDE.md` concise; route to doctrine instead of duplicating it.
- Prefer existing manifests and canonical examples over improvisation.
- Respect `docker-compose.yml` and `docker-compose.test.yml` as the standard filenames.
- Keep dev data and test data strictly isolated.
