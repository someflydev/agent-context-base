# CLAUDE.md

Use this file as a boot entrypoint, not as the full source of truth.

Follow [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) before broad exploration.

## First Reads

1. [`README.md`](README.md)
2. [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md)
3. [`docs/runtime-state-workflow.md`](docs/runtime-state-workflow.md)
4. run `python3 scripts/work.py resume`
5. `memory/INDEX.md` (if resuming work or starting a new prompt)
6. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
7. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
8. [`docs/repo-layout.md`](docs/repo-layout.md)

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
- Treat `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, and `context/MEMORY.md` as local runtime state, not doctrine.
- After `work.py resume`, use its git anchor, recent-change clues, next-step signal, and plan-review signal to decide what to read next. Then read `context/TASK.md`, then `context/SESSION.md`, then `context/MEMORY.md` only if durable repo-local truths matter.
- After `work.py resume`, check `memory/INDEX.md` and load any `memory/summaries/` artifact relevant to the current work before starting task-specific context loading.
- Prefer manifests, canonical examples, and validation gates over improvisation.
- Treat templates as scaffolds, not canonical truth.
- Use `python3 scripts/work.py checkpoint` after meaningful changes, before ending a session, and before a likely handoff.
- Update `PLAN.md` only when a `.prompts` megaprompt or major decision materially changes phases or milestones.
- If a repo provides `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`, or `context/MEMORY.example.md`, `init` and `checkpoint` will scaffold missing runtime files from those examples.
- Do not claim completion without running the stated proof path.
- If proof is unavailable, report the work as `blocked` or `incomplete` instead of `done`.

## Verification

Verification scripts use `unittest`, not `pytest`.

```bash
python scripts/run_verification.py --tier fast
python scripts/validate_context.py
python .acb/scripts/acb_verify.py
```
