# {{repo_name}}

{{description}}

## Start Here

1. Read `AGENT.md` or `CLAUDE.md`
2. Read `docs/repo-purpose.md`
3. Read `docs/repo-layout.md`
4. Read `manifests/project-profile.yaml`
5. Read `.generated-profile.yaml`

If `MEMORY.md` exists, read it after the stable startup files and a narrow repo-signal check.

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack_display}}`
- selected manifests: `{{selected_manifests}}`
- Dokku support: `{{dokku_status}}`
- prompt-first support: `{{prompt_first_status}}`

## Common Workflows

{{workflow_bullets}}

## Verification Posture

- smoke tests live under `tests/smoke/`
- integration tests live under `tests/integration/` when a real boundary exists
- destructive reset flows must target `docker-compose.test.yml` only

## Continuity

- use `MEMORY.md` when work will span sessions
- use handoff snapshots for durable transfer points

{{compose_section}}

{{dokku_section}}
