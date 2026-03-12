# Session Start

Use this file when beginning a new task or returning to a long-lived repo after context drift.

## Read First

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `context/router/task-router.md`

## Fast Checks

- run `python scripts/validate_context.py` if metadata, examples, routing, or bootstrap behavior changed
- run `python scripts/prompt_first_repo_analyzer.py .` if the active stack or archetype is unclear
- run `python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors` when a manifest already looks close

## Recommended Anchor Pairings

- general routing ambiguity: `context/anchors/session-start.md`
- integrity or metadata work: `context/anchors/context-integrity.md`
- Compose or infra work: `context/anchors/compose-isolation.md`
- prompt files or prompt-first repo work: `context/anchors/prompt-first.md`

## Stop Early When

- the task still needs more than one primary workflow after routing
- the repo signals disagree with the current manifest choice
- storage or deployment behavior changed but no smoke or integration path exists
- the change would require loading multiple near-match examples

Use `context/doctrine/stop-conditions.md` as the explicit guardrail reference.
