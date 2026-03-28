# Session Start

Use this checklist when starting or resuming work.

## Read First

1. `AGENT.md` or `CLAUDE.md`
2. `python3 scripts/work.py resume` when the repo has a root `scripts/` directory, or `python3 .acb/scripts/work.py resume` in compact derived repos
3. `context/TASK.md` and `context/SESSION.md` when they exist
4. `context/MEMORY.md` only if durable repo-local truths matter
5. `PLAN.md` when milestone context matters
6. `.acb/SESSION_BOOT.md` when present
7. `.acb/profile/selection.json` when present
8. `.acb/specs/AGENT_RULES.md` and `.acb/specs/VALIDATION.md` when present
9. `.acb/validation/CHECKLIST.md` and `.acb/validation/COVERAGE.md` when present
10. `README.md` and `docs/` only when they exist and are clearly current

## Quick Commands

```bash
python3 scripts/work.py status
python3 scripts/work.py checkpoint
python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors
python scripts/validate_context.py
python .acb/scripts/acb_inspect.py
python .acb/scripts/acb_verify.py
```

## Stop Early When

- more than one workflow or stack still looks primary
- repo signals and the chosen profile disagree
- the proof path is unclear
- drift or coverage gaps changed the startup truth
