# {{repo_name}}

{{description}}

## Start Here

1. Read `AGENT.md` or `CLAUDE.md`
2. Read `docs/repo-purpose.md`
3. Read `docs/repo-layout.md`
4. Read `manifests/project-profile.yaml`

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack_display}}`
- selected manifests: `{{selected_manifests}}`
- Dokku support: `{{dokku_status}}`
- prompt-first support: `{{prompt_first_status}}`

## Common Workflows

{{workflow_bullets}}

## Testing Posture

- smoke tests live under `tests/smoke/`
- integration tests live under `tests/integration/` when a real boundary exists
- destructive test reset flows must target `docker-compose.test.yml` only

{{compose_section}}

{{dokku_section}}

