# Session Start

Use this checklist when starting or resuming work.

## Read First

1. `AGENT.md` or `CLAUDE.md`
2. `.acb/SESSION_BOOT.md` when present
3. `.acb/profile/selection.json` when present
4. `.acb/specs/AGENT_RULES.md` and `.acb/specs/VALIDATION.md` when present
5. `.acb/validation/CHECKLIST.md` and `.acb/validation/COVERAGE.md` when present
6. `README.md` and `docs/` only when they exist and are clearly current
7. `MEMORY.md` only after that stable startup pass

## Quick Commands

```bash
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
