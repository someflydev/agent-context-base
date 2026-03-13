# AGENT.md

Purpose: boot the assistant into the smallest useful context bundle for this repo.

## First Reads

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `manifests/project-profile.yaml`
5. `.generated-profile.yaml`

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack}}`
- selected manifests: `{{selected_manifests}}`

## Bundle Discipline

Load only:

1. the relevant doctrine
2. one workflow
3. the active stack or archetype guidance
4. one canonical example

## Guardrails

- keep this file concise
- treat `MEMORY.md` as continuity only
- update `MEMORY.md` at meaningful stop points
- create a handoff snapshot when another session is likely
- stop when stack, archetype, or Compose isolation ambiguity would cause context sprawl
- `docker-compose.test.yml` is the only target for destructive test reset flows
