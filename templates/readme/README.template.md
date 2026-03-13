# {{repo_name}}

{{description}}

## Start Here

1. Read `AGENT.md` or `CLAUDE.md`
2. Read `docs/repo-purpose.md`
3. Read `docs/repo-layout.md`
4. Read `manifests/project-profile.yaml`

If `MEMORY.md` exists, read it after the stable startup files and basic repo-signal checks.

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack_display}}`
- selected manifests: `{{selected_manifests}}`
- Dokku support: `{{dokku_status}}`
- prompt-first support: `{{prompt_first_status}}`

## Continuity

- use `MEMORY.md` for current-task continuity when work spans sessions
- use handoff snapshots for durable checkpoints when a later session or another assistant will continue

## Common Workflows

{{workflow_bullets}}

## Testing Posture

- smoke tests live under `tests/smoke/`
- integration tests live under `tests/integration/` when a real boundary exists
- destructive test reset flows must target `docker-compose.test.yml` only

{{compose_section}}

{{dokku_section}}
