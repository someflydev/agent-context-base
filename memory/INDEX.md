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
- `memory/summaries/PROMPT_95_completion.md` — completion summary for the verification-hardening arc closeout
- `memory/summaries/PROMPT_97_completion.md` — completion summary for startup trace protocol work
- `memory/summaries/PROMPT_91_through_95_arc_summary.md` — local arc summary for the explicit memory and operator-console upgrade
- `memory/summaries/PROMPT_99_completion.md` — local completion summary for startup feature toggleability and arc closeout
- `memory/summaries/PROMPT_96_through_99_arc_summary.md` — local arc summary for startup trace, pseudo-logging, and context validation
- `memory/summaries/PROMPT_107_completion.md` — local completion summary for the terminal tooling Phase 1 hardening pass
- `memory/summaries/PROMPT_100_through_107_phase1_summary.md` — local arc summary for the terminal tooling Phase 1 buildout and hardening

## Terminal Tooling Arc (PROMPT_100-111)

- **Doctrine**: `context/doctrine/terminal-ux-first-class.md` — 10 rules
- **Archetypes**: `terminal-tui.md`, `terminal-dual-mode.md`
- **Stacks**: 14 stacks in `context/stacks/terminal-*.yaml`
- **Validation contract**: `docs/terminal-validation-contract.md`
- **Examples**: `examples/canonical-terminal/` (14 examples, 7 languages)
- **Catalog**: `examples/canonical-terminal/CATALOG.md`
- **Decision guide**: `examples/canonical-terminal/DECISION_GUIDE.md`
- **Phase 1 summary**:
  `memory/summaries/PROMPT_100_through_107_phase1_summary.md`
- **Phase 1 completion**: `memory/summaries/PROMPT_107_completion.md`

## Contributing

Add to `memory/concepts/` when a finding is durable, curated, and worth committing for
future assistants. Write to `memory/summaries/` and `memory/sessions/` freely during a
session — they are local-only and will not be committed automatically. Keep
`context/MEMORY.md` for live current-task state. Use `artifacts/handoffs/` for
general-purpose timestamped transfer snapshots you want committed.
