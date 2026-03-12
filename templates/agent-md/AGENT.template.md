# AGENT.md

Purpose: route the assistant to the smallest relevant context bundle for the current repo.

## First Reads

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `manifests/project-profile.yaml`
5. `.generated-profile.yaml`

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack}}`
- selected manifests: `{{selected_manifests}}`

## Routing Rule

Infer the task from normal language, then load:

1. only the relevant doctrine
2. one primary workflow
3. the generated project profile and the stack notes tied to the active change
4. one preferred canonical example

## Guardrails

- keep this file concise
- do not duplicate doctrine here
- stop when stack or archetype ambiguity would cause context sprawl
- `docker-compose.test.yml` is the only target for destructive test reset flows
- prefer exact filename references in prompts and implementation requests
