# Assistant Behavior Specification

This is the normative behavior contract for assistants working in this repo and repos derived from it.

Normative language:

- `MUST`: required
- `SHOULD`: expected unless there is a concrete repo-specific reason to differ
- `MUST NOT`: prohibited

## Required Behavior

- The assistant MUST follow [`docs/context-boot-sequence.md`](../context-boot-sequence.md) before broad exploration.
- The assistant MUST use `scripts/work.py resume` at session start when the repo has a root `scripts/` directory, or `.acb/scripts/work.py resume` in compact derived repos without one.
- The assistant MUST re-read `.acb/` startup files at the beginning of each new session in generated repos.
- The assistant MUST prefer one workflow, one active stack surface, one archetype when needed, and one canonical example.
- The assistant MUST use validation gates and checklists when they exist.
- The assistant MUST validate before claiming completion unless the operator explicitly waives validation.
- The assistant MUST distinguish `blocked`, `incomplete`, and `done`.
- The assistant MUST treat `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, `context/MEMORY.md`, and handoff files as continuity artifacts, never as doctrine.
- The assistant MUST keep `PLAN.md` for roadmap-level changes and use `context/TASK.md` plus `context/SESSION.md` for in-phase progress.

## Prohibited Behavior

- The assistant MUST NOT start by scanning whole directories.
- The assistant MUST NOT treat templates as canonical examples.
- The assistant MUST NOT report completion based on plausible code generation alone.
- The assistant MUST NOT bypass validation silently.
- The assistant MUST NOT pretend to know live token-window usage when only repo-local heuristics are available.

## Planning And Execution

- The assistant SHOULD name the active boundary, proof path, and stop conditions before substantial work.
- The assistant SHOULD keep implementation, docs, and validation aligned in the same slice when the truth changed.
- The assistant SHOULD surface drift or coverage gaps when `.acb/INDEX.json` or `.acb/validation/COVERAGE.json` indicate them.
- The assistant SHOULD run `work.py checkpoint` after meaningful changes, before ending a session, and when a fresh handoff is likely.
