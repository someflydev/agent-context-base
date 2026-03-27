# CLAUDE.md

Use this file as a boot entrypoint, not as the full source of truth.

Follow [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) before broad exploration.

## First Reads

1. [`README.md`](README.md)
2. [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md)
3. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
4. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
5. [`docs/repo-layout.md`](docs/repo-layout.md)

## Minimal Context Policy

Prefer this order:

1. one router
2. one workflow
3. one active stack surface
4. one archetype if the repo shape matters
5. one canonical example
6. spec/validation modules only when working on `.acb/` composition or hardening

Load one dominant path, not a broad survey.

## Guardrails

- Re-read generated `.acb/` boot files at session start.
- Prefer manifests, canonical examples, and validation gates over improvisation.
- Treat templates as scaffolds, not canonical truth.
- Do not claim completion without running the stated proof path.
- If proof is unavailable, report the work as `blocked` or `incomplete` instead of `done`.

## Verification

Verification scripts use `unittest`, not `pytest`.

```bash
python scripts/run_verification.py --tier fast
python scripts/validate_context.py
python .acb/scripts/acb_verify.py
```
