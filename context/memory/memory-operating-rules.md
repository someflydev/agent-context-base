# Memory Operating Rules

Use this file as the operational playbook for assistant continuity behavior.

## Core Rules

- read `MEMORY.md` early if it exists, after stable boot anchors and repo signals
- treat `MEMORY.md` as current-task continuity, not as doctrine
- prefer code and tests over `MEMORY.md` for implementation reality
- prefer doctrine over `MEMORY.md` for policy, rules, and operating constraints
- update `MEMORY.md` at meaningful stop points, not after every small action
- prune or rewrite stale sections instead of endlessly appending
- keep memory focused on the current task or current prompt batch
- use explicit file paths and explicit prompt filenames
- capture `Explicitly Not Doing` whenever scope control matters
- capture the active working set whenever practical

## Read Order

Use this runtime order:

1. stable startup files such as `AGENT.md`, `CLAUDE.md`, boot docs, and repo layout
2. repo signals and routing files
3. `MEMORY.md` if present
4. latest relevant handoff snapshot if the task is clearly a resumed transfer
5. minimal task context from doctrine, workflows, manifests, stacks, archetypes, and examples

This keeps memory useful without letting it bypass routing.

## How To Use `MEMORY.md`

Use `MEMORY.md` to reduce reload cost by capturing:

- current objective
- current working set
- already inspected files
- decisions already made
- explicitly ruled-out work
- next concrete steps

Do not use `MEMORY.md` to skip:

- reading the relevant doctrine
- checking the actual code
- verifying prompt numbering
- validating smoke-test or integration-test requirements
- confirming deployment or Compose constraints

## Working-Set Discipline

When practical, keep `Active Working Set` limited to the files most likely to matter next.

Good working sets:

- 3 to 10 files for a medium task
- explicit paths
- changed as the task changes phase

Bad working sets:

- large directory globs
- every file inspected during the whole task
- vague labels such as "router files" or "prompt stuff"

## Scope Control

Use `Explicitly Not Doing` when adjacent work could create scope drift.

Common examples:

- not renumbering existing prompt files
- not redesigning manifest structure
- not broadening a smoke test into a full integration suite
- not changing deployment wiring during a local-only fix

Scope notes should be brief and active.

## Freshness And Pruning

Prune aggressively.

Signs the file needs rewriting:

- next steps refer to work that is already complete
- the working set no longer matches the current phase
- blockers are resolved but still listed
- stale findings require rereading to understand what still matters
- the file reads like a transcript

If the file is getting long, rewrite it into the smallest current-state summary.

## Prompt-First Compatibility

For prompt-first repos, also record:

- highest completed prompt filename
- next intended prompt filename
- numbering decisions already made
- prompts intentionally deferred or skipped

Rules:

- use exact filenames such as `.prompts/005-add-smoke-surface.txt`
- keep numbering strictly monotonic
- do not use memory notes to justify renumbering later
- do not refer to prompts vaguely when filenames are known

## Relationship To The Context Complexity Budget

`MEMORY.md` can act as a compressed checkpoint that reduces unnecessary rescanning in later turns.

That is useful because it lowers reload cost inside the context complexity budget.

But memory does not authorize broader loading by itself.

It should:

- reduce repeated repo scanning
- reduce duplicate file inspection
- reduce restatement of already settled scope

It should not:

- bypass doctrine
- replace manifest selection
- skip code verification
- justify loading extra unrelated context

## Handoff Rule

When the pause is meaningful and likely to cross sessions, create a handoff snapshot in addition to refreshing `MEMORY.md`.

Use `MEMORY.md` for live continuity.

Use handoff snapshots for durable transfer.

## 3-Tier Memory Base

The committed `memory/` directory is the structured knowledge base for this repo. It
holds durable findings, session notes, and prompt-boundary summaries that survive across
sessions and are visible to any future assistant. Unlike `context/MEMORY.md`, everything
here is committed and version-controlled.

**Load order:**

1. `memory/INDEX.md` first — orientation only, after `work.py resume`
2. `memory/summaries/PROMPT_XX_resume.md` or `PROMPT_XX_completion.md` — for the specific
   prompt being resumed or continued
3. `memory/concepts/<slug>.md` — when working in a known problem domain

**Commit status of each tier:**

- `memory/concepts/` — committed; the only tier in memory/ that belongs in version control
- `memory/sessions/` — gitignored; local-only, generated freely during a session
- `memory/summaries/` — gitignored; local-only, prompt-boundary checkpoints

**When to prefer `memory/` over `context/MEMORY.md`:**

- Use `memory/summaries/` for a prompt-boundary checkpoint (local, not committed)
- Use `memory/concepts/` when a finding is durable, curated, and worth committing
- Use `context/MEMORY.md` for live current-task state that changes constantly

**When to add to `memory/concepts/` vs update `context/MEMORY.md`:**

- Add to `memory/concepts/` after the second time you look something up and wish it were
  written down, or after resolving a non-obvious confusion that affected implementation;
  these will be committed and visible to future sessions
- Update `context/MEMORY.md` for active-task continuity that will be pruned when done

For the full compaction model, see
`context/doctrine/memory-compaction-discipline.md`.
