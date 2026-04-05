# {{repo_name}}

{{description}}

This README should stay factual and small. Expand it only when the repo has enough implemented surface to support honest public-facing documentation.

## Start Here

1. Read `AGENT.md` or `CLAUDE.md`
2. Read `{{repo_local_profile_path}}`
3. Read `{{generated_profile_path}}`
4. Run `python3 scripts/work.py resume` when the repo has a root `scripts/` directory; otherwise use `python3 .acb/scripts/work.py resume`
5. Read `docs/repo-purpose.md` if it exists
6. Read `docs/repo-layout.md` if it exists

Read `context/TASK.md` and `context/SESSION.md` after the stable startup files. Read `context/MEMORY.md` only when durable repo-local truths matter. Read `PLAN.md` when milestone context matters. Read `tmp/*.md` only when there is an active local checklist or ad hoc session plan relevant to the task.

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

- use `python3 scripts/work.py checkpoint` at natural boundaries when the root script exists; otherwise use `python3 .acb/scripts/work.py checkpoint`
- keep `PLAN.md` for roadmap-level phase changes, `context/TASK.md` for the active slice, `context/SESSION.md` for compact handoff state, and `context/MEMORY.md` for durable local truths
- keep prompt-session checklists or ad hoc work plans in `tmp/*.md`
- repos may customize missing runtime-note scaffolds with `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`, and `context/MEMORY.example.md`
- use handoff snapshots for durable transfer points
- keep front-facing docs earned by implementation, not speculation

{{compose_section}}

{{dokku_section}}
