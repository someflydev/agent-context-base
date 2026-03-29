# AGENT.md

Purpose: boot an assistant into the smallest useful context bundle for this repo.

Read [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) first. This repo now has a canonical spec/validation layer for `.acb/` generation, plus a repo-local runtime-state workflow for session restart and checkpointing.

## First Reads

1. [`README.md`](README.md)
2. [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md)
3. [`docs/runtime-state-workflow.md`](docs/runtime-state-workflow.md)
4. run `python3 scripts/work.py resume`
5. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
6. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
7. [`docs/repo-layout.md`](docs/repo-layout.md)
8. one router, one workflow, one stack, and one example only if the task still needs narrowing

## Operating Rules

- Treat `.acb/` as the generated repo-local operating boundary.
- Treat `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, and `context/MEMORY.md` as local runtime state, not doctrine.
- After `work.py resume`, use its git anchor, recent-change clues, next-step signal, and plan-review signal to decide what to read next. Then read `context/TASK.md` and `context/SESSION.md`; read `context/MEMORY.md` only when durable repo-local truths matter; read `PLAN.md` only when milestone context matters.
- When working in a generated repo, re-read `.acb/SESSION_BOOT.md`, `.acb/profile/selection.json`, `.acb/specs/AGENT_RULES.md`, and `.acb/specs/VALIDATION.md` at session start.
- Prefer manifest-defined bundles over improvised loading.
- Validation is mandatory before claiming completion unless the operator explicitly waives it.
- Use `blocked`, `incomplete`, and `done` precisely.
- Use `python3 scripts/work.py checkpoint` at natural boundaries.
- Update `PLAN.md` only when a `.prompts` megaprompt or a major decision materially reshapes phases, milestones, or the near-to-mid-term roadmap.
- Keep `context/MEMORY.md` durable and clean; keep active-step detail in `context/TASK.md` and `context/SESSION.md`.
- If a repo provides `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`, or `context/MEMORY.example.md`, `init` and `checkpoint` will use those as scaffold sources for missing runtime files.

## New Repo Routing

- When started in `agent-context-base`, assume the operator wants a new generated repo unless they explicitly say they want to modify the base repo itself.
- For new generated repos, prefer `scripts/new_repo.py` over manual scaffolding.
- Make storage, queue, search, and deployment assumptions explicit before generation.
- Pass the operator prompt through `--initial-prompt-text` or `--initial-prompt-file` whenever possible.

## Verification

- Base repo: `python scripts/validate_context.py`
- Generated repo: `python .acb/scripts/acb_verify.py`
- Inspect payload: `python .acb/scripts/acb_inspect.py`
