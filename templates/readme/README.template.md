# {{repo_name}}

{{description}}

This README should stay factual and small. Expand it only when the repo has enough implemented surface to support honest public-facing documentation.

## Start Here

1. Read `AGENT.md` or `CLAUDE.md`
2. Read `{{repo_local_profile_path}}`
3. Read `{{generated_profile_path}}`
4. Read `docs/repo-purpose.md` if it exists
5. Read `docs/repo-layout.md` if it exists

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
- keep front-facing docs earned by implementation, not speculation

{{compose_section}}

{{dokku_section}}
