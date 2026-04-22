# Session Start

Read first: see [`docs/context-boot-sequence.md`](context-boot-sequence.md).

## Quick Commands

```bash
python3 scripts/work.py status
python3 scripts/work.py checkpoint
python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors
python scripts/validate_context.py
python .acb/scripts/acb_inspect.py
python .acb/scripts/acb_verify.py
```

`resume` and `status` now surface recent git anchors, changed-file clues, a best-effort next step from runtime notes, and modest plan-review or memory-promotion hints. Use those signals to decide whether runtime files need review before reading deeper.

## Stop Early When

- more than one workflow or stack still looks primary
- repo signals and the chosen profile disagree
- the proof path is unclear
- drift or coverage gaps changed the startup truth
