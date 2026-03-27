# Session Start

Use this checklist when starting a task or resuming after context drift.

## Read First

1. `AGENT.md` or `CLAUDE.md`
2. `.acb/manifests/project-profile.yaml` when present, otherwise `manifests/project-profile.yaml`
3. `.acb/.generated-profile.yaml` when present, otherwise `.generated-profile.yaml`
4. `README.md` if it exists and is current
5. `docs/context-boot-sequence.md`
6. `docs/repo-purpose.md` if it exists
7. `docs/repo-layout.md` if it exists
8. `context/router/task-router.md`

Then inspect narrow repo signals. Read `MEMORY.md` only after that stable startup pass.

## Quick Actions

- `python scripts/prompt_first_repo_analyzer.py .` when the stack or archetype is unclear
- `python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors` when a manifest looks close
- `python scripts/validate_context.py` when manifests, examples, routing, or templates changed
- `python scripts/check_memory_freshness.py` when resuming a longer task with an existing `MEMORY.md`
- `python scripts/init_memory.py` when a non-trivial task needs a new continuity file

## Useful Anchors

- `context/anchors/repo-identity.md`
- `context/anchors/context-loading-principles.md`
- `context/anchors/anti-patterns.md`
- `context/anchors/context-integrity.md` for metadata work
- `context/anchors/compose-isolation.md` for infra work
- `context/anchors/prompt-first.md` for prompt-first repos
- `context/doctrine/documentation-timing-discipline.md` when deciding whether front-facing docs should exist yet

## Stop Early When

- more than one workflow still looks primary
- repo signals and the chosen manifest disagree
- a storage or deployment change has no verification path
- the next step would require loading multiple near-match examples

Use `context/doctrine/stop-conditions.md` as the final guardrail. Update `MEMORY.md` at meaningful pause points.
