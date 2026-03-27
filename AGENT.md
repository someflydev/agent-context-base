# AGENT.md

Purpose: boot an assistant into the smallest useful context bundle for this repo.

Read [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md) first. This repo now has a canonical spec/validation layer for `.acb/` generation, so do not treat older context docs as the only source of truth.

## First Reads

1. [`README.md`](README.md)
2. [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md)
3. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
4. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
5. [`docs/repo-layout.md`](docs/repo-layout.md)
6. one router, one workflow, one stack, and one example only if the task still needs narrowing

## Operating Rules

- Treat `.acb/` as the generated repo-local operating boundary.
- When working in a generated repo, re-read `.acb/SESSION_BOOT.md`, `.acb/profile/selection.json`, `.acb/specs/AGENT_RULES.md`, and `.acb/specs/VALIDATION.md` at session start.
- Prefer manifest-defined bundles over improvised loading.
- Validation is mandatory before claiming completion unless the operator explicitly waives it.
- Use `blocked`, `incomplete`, and `done` precisely.
- Use `MEMORY.md` only for continuity, never as doctrine.

## New Repo Routing

- When started in `agent-context-base`, assume the operator wants a new generated repo unless they explicitly say they want to modify the base repo itself.
- For new generated repos, prefer `scripts/new_repo.py` over manual scaffolding.
- Make storage, queue, search, and deployment assumptions explicit before generation.
- Pass the operator prompt through `--initial-prompt-text` or `--initial-prompt-file` whenever possible.

## Verification

- Base repo: `python scripts/validate_context.py`
- Generated repo: `python .acb/scripts/acb_verify.py`
- Inspect payload: `python .acb/scripts/acb_inspect.py`
