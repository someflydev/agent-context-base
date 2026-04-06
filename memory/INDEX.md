# Memory Index

## Purpose

`memory/` is the structured knowledge base for `agent-context-base`. It is NOT a
replacement for `context/MEMORY.md` (local, mutable, task-scoped), NOT a replacement for
doctrine in `context/doctrine/` (policy and rules), and NOT `artifacts/handoffs/`
(general-purpose timestamped snapshots).

The tiers have different commit profiles:

- `memory/concepts/` — **committed**. Curated, durable, slow-changing facts deliberately
  added after multiple sessions.
- `memory/sessions/` — **gitignored**. Local session logs generated during a session.
  Raw, ephemeral, not reviewed before commit.
- `memory/summaries/` — **gitignored**. Local prompt-boundary checkpoints. Generated
  per session; accumulate quickly; not commit-worthy by default.

## When To Read This

Read `memory/INDEX.md` after `work.py resume` output and after reading `context/TASK.md` /
`context/SESSION.md` — but before starting task-specific context loading. Specifically:
- When resuming interrupted work on a specific prompt, check `memory/summaries/` first
- When encountering a known problem domain, check `memory/concepts/` next
- Do not read this before `work.py resume`; that wastes context on orientation before routing

## Tier Map

| Directory      | Committed? | Purpose                                                          |
|----------------|------------|------------------------------------------------------------------|
| `concepts/`    | yes        | Durable knowledge: stable conventions, recurring patterns, pitfalls |
| `sessions/`    | no         | Session logs: exploration traces, prompt execution notes          |
| `summaries/`   | no         | Prompt-boundary checkpoints and resume handoffs                   |

## Load Priority

1. **`summaries/` first** — when resuming a specific prompt or returning after a pause,
   check for `PROMPT_XX_resume.md` or `PROMPT_XX_completion.md` matching your current work
2. **`concepts/` next** — when working on a known domain (prompt sequencing, memory model,
   .acb composition, verification gates), load the relevant concept file
3. **`sessions/` rarely** — only when tracing a specific past decision not captured in
   concepts or summaries

## Current Contents

- `memory/concepts/README.md` — guide to the concepts tier
- `memory/concepts/canonical-example-selection.md` — quick orientation for how this repo chooses canonical examples
- `memory/concepts/prompt-numbering-discipline.md` — strict prompt numbering and filename rules
- `memory/concepts/verification-gate-overview.md` — fast orientation for the main verification commands
- `memory/sessions/README.md` — guide to the sessions tier (gitignored; no files yet)
- `memory/summaries/README.md` — guide to the summaries tier (gitignored)
- `memory/summaries/PROMPT_90_completion.md` — committed format example (tracked before gitignore was added)
- `memory/summaries/PROMPT_93_completion.md` — prompt-boundary summary for the prompt-meta-runner and workflow update

## Contributing

Add to `memory/concepts/` when a finding is durable, curated, and worth committing for
future assistants. Write to `memory/summaries/` and `memory/sessions/` freely during a
session — they are local-only and will not be committed automatically. Keep
`context/MEMORY.md` for live current-task state. Use `artifacts/handoffs/` for
general-purpose timestamped transfer snapshots you want committed.
