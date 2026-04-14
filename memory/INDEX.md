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

## Terminal Tooling Arc (PROMPT_100-111)

- **Doctrine**: `context/doctrine/terminal-ux-first-class.md` — 10 rules
- **Archetypes**: `terminal-tui.md`, `terminal-dual-mode.md`
- **Stacks**: 14 stacks in `context/stacks/terminal-*.yaml`
- **Validation contract**: `docs/terminal-validation-contract.md`
- [Terminal Example Selection](../context/skills/terminal-example-selection.md) — select CLI/TUI/dual-mode examples
- [Terminal Validation Path Selection](../context/skills/terminal-validation-path-selection.md) — choose terminal test approach
- **Examples**: `examples/canonical-terminal/` (14 examples, 7 languages)
- **Catalog**: `examples/canonical-terminal/CATALOG.md`
- **Decision guide**: `examples/canonical-terminal/DECISION_GUIDE.md`

## Schema Validation Arc

- [Schema Validation Doctrine](../context/doctrine/schema-validation-contracts.md) — three-lane model: runtime / contract / hybrid
- [Schema Validation Lane Selection](../context/skills/schema-validation-lane-selection.md) — route to Lane A/B/C per language
- [Contract Generation Path Selection](../context/skills/contract-generation-path-selection.md) — schema export + drift detection
- [Schema Validation Stacks](../context/stacks/) — `schema-validation-{language}.yaml` for 7 languages
- [Polyglot Validation Lab Archetype](../context/archetypes/polyglot-validation-lab.md) — cross-language validation comparison surface
- [Domain Model Spec](../examples/canonical-schema-validation/domain/models.md) — WorkspaceSyncContext: 5 models, 23 fixtures
- [Parity Rules](../examples/canonical-schema-validation/PARITY.md) — cross-language consistency contract
- [Example Catalog](../examples/canonical-schema-validation/CATALOG.md) — all 18 examples [x] by language, library, lane (PROMPT_117)
- [Arc Overview](../docs/schema-validation-arc-overview.md) — single-read arc summary for future sessions
- [Drift Detection Guide](../docs/schema-validation-drift-detection.md) — CI strategies for schema drift
- [Arc Durable Knowledge](../memory/concepts/schema-validation-arc.md) — committed facts about the arc

## Faker and Synthetic Data Generation Arc

- [Arc Overview](../docs/faker-arc-overview.md) — single-read arc summary for future sessions
- [Doctrine](../context/doctrine/synthetic-data-realism.md) — 7 generation rules
- [Domain Spec](../examples/canonical-faker/domain/schema.md) — TenantCore entity graph
- [CATALOG](../examples/canonical-faker/CATALOG.md) — all 10 examples (all [x] as of PROMPT_125)
- [Arc Durable Knowledge](../memory/concepts/faker-arc.md) — committed facts about the arc

## Contributing

Add to `memory/concepts/` when a finding is durable, curated, and worth committing for
future assistants. Write to `memory/summaries/` and `memory/sessions/` freely during a
session — they are local-only and will not be committed automatically. Keep
`context/MEMORY.md` for live current-task state. Use `artifacts/handoffs/` for
general-purpose timestamped transfer snapshots you want committed.
