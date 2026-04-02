# Memory Index

## Purpose

`memory/` is the committed, structured knowledge base for `agent-context-base`. It holds
durable findings, session notes, and prompt-boundary summaries that should survive across
sessions and be visible to any assistant picking up this work. It is NOT a replacement for
`context/MEMORY.md` (which is local, mutable, and task-scoped), NOT a replacement for
doctrine files in `context/doctrine/` (which define policy and rules), and NOT an archive
of `artifacts/handoffs/` snapshots (which are general-purpose transfer artifacts). Everything
here is committed, version-controlled, and structured by purpose.

## When To Read This

Read `memory/INDEX.md` after `work.py resume` output and after reading `context/TASK.md` /
`context/SESSION.md` — but before starting task-specific context loading. Specifically:
- When resuming interrupted work on a specific prompt, check `memory/summaries/` first
- When encountering a known problem domain, check `memory/concepts/` next
- Do not read this before `work.py resume`; that wastes context on orientation before routing

## Tier Map

| Directory      | Purpose                                                                 |
|----------------|-------------------------------------------------------------------------|
| `concepts/`    | Durable knowledge: stable conventions, recurring patterns, known pitfalls |
| `sessions/`    | Session notes: exploration logs, prompt execution notes, decision records |
| `summaries/`   | Compacted artifacts: prompt-boundary checkpoints, resume handoffs        |

## Load Priority

1. **`summaries/` first** — when resuming a specific prompt or returning after a pause,
   check for `PROMPT_XX_resume.md` or `PROMPT_XX_completion.md` matching your current work
2. **`concepts/` next** — when working on a known domain (prompt sequencing, memory model,
   .acb composition, verification gates), load the relevant concept file
3. **`sessions/` rarely** — only when tracing a specific past decision not captured in
   concepts or summaries

## Current Contents

- `memory/concepts/README.md` — guide to the concepts tier (no concept files yet)
- `memory/sessions/README.md` — guide to the sessions tier (no session files yet)
- `memory/summaries/README.md` — guide to the summaries tier
- `memory/summaries/PROMPT_90_completion.md` — canonical example of a completion summary

## Contributing

Add to `memory/` rather than `context/MEMORY.md` when: the finding is durable across
sessions, the content should be version-controlled and visible to any future assistant, or
you are at a prompt boundary and want to preserve a compaction artifact. Keep
`context/MEMORY.md` for live, current-task state. Keep `artifacts/handoffs/` for
general-purpose timestamped transfer snapshots. Use `memory/summaries/` for
prompt-boundary checkpoints and `memory/concepts/` for stable knowledge that will be
relevant to future prompts.
