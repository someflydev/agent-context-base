# AGENT.md

Purpose: route the assistant to the smallest relevant context bundle for the current repo.

## First Reads

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `context/router/task-router.md`

## Routing Rule

Infer the task from normal language, then load:

1. only the relevant doctrine
2. one primary workflow
3. the needed archetype and stack files
4. one preferred canonical example

## Guardrails

- keep this file concise
- do not duplicate doctrine here
- stop when stack or archetype ambiguity would cause context sprawl

