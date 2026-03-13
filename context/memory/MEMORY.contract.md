# MEMORY.md Contract

`MEMORY.md` is the runtime working-state artifact for the current task.

It exists to preserve continuity across long sessions, fresh assistant restarts, interrupted work, and human or assistant handoffs without turning the repo into a running transcript.

Use this contract together with:

- `context/memory/memory-operating-rules.md`
- `context/memory/stop-hook-guidance.md`
- `context/memory/handoff-snapshots.md`
- `docs/memory-layer-overview.md`

## Purpose

`MEMORY.md` should answer the small set of questions a fresh assistant session needs before it starts rescanning files:

- What is the current objective?
- What stack, archetype, or prompt-first shape has already been inferred?
- Which files are the active working set?
- Which files were already inspected?
- What important findings or constraints were discovered?
- What decisions were already made?
- What is explicitly not in scope?
- What blockers or risks remain?
- What are the next concrete steps?
- What stop condition defines the next pause point?

## What Belongs In `MEMORY.md`

Keep only current-task operational state such as:

- the current objective in one or two sentences
- inferred stack, archetype, manifest, or prompt batch when that inference matters
- the active working set of files likely to be touched next
- files already inspected so the next session can avoid rescanning blindly
- important findings discovered during implementation or repo inspection
- decisions already made, including rejected options when they materially constrain the next step
- explicitly not doing, when scope control matters
- blockers, risks, failed validations, or missing information that shape the next move
- next steps written as concrete actions
- a stop condition describing what counts as the next meaningful checkpoint
- a short last-updated marker

## What Does Not Belong In `MEMORY.md`

Do not turn `MEMORY.md` into:

- a copy of doctrine
- a manifest substitute
- a canonical example substitute
- a design document for future possibilities
- a diary of every command or thought
- a changelog of every file edit
- a dump of copied code or copied prompt bodies
- a replacement for issue tracking, tickets, or durable architecture docs
- a place to restate large parts of `AGENT.md`, `CLAUDE.md`, workflow docs, or the operating manual

If a detail is stable and repo-wide, it belongs in doctrine, workflow docs, manifests, examples, code comments, or normal documentation instead.

## Authority And Precedence

Use this precedence order:

1. code and tests describe implementation reality
2. doctrine describes stable policy and operating constraints
3. manifests describe structured context selection
4. canonical examples describe preferred implementation shape
5. `MEMORY.md` describes current operational state

`MEMORY.md` is useful because it is current, not because it outranks other artifacts.

When `MEMORY.md` conflicts with doctrine, follow doctrine.

When `MEMORY.md` conflicts with the codebase, inspect the code and update `MEMORY.md`.

## Recommended Sections

Use these sections in roughly this order:

```md
# MEMORY.md

## Current Objective
## Current Context
## Active Working Set
## Files Already Inspected
## Important Findings
## Decisions Already Made
## Explicitly Not Doing
## Blockers Or Risks
## Next Steps
## Stop Condition
## Last Updated
```

Recommended content by section:

- `Current Objective`: the current task only, not the whole repo mission
- `Current Context`: active stack, archetype, manifest, prompt file, or deployment posture when useful
- `Active Working Set`: exact file paths expected to be touched or revisited next
- `Files Already Inspected`: exact file paths already reviewed enough to avoid reloading first
- `Important Findings`: facts learned from the repo or validation runs
- `Decisions Already Made`: choices already locked for this task
- `Explicitly Not Doing`: scope guardrails and ruled-out adjacent work
- `Blockers Or Risks`: failed tests, unanswered questions, deployment concerns, stale assumptions
- `Next Steps`: 2 to 5 concrete actions
- `Stop Condition`: the next checkpoint that should trigger a memory refresh or handoff
- `Last Updated`: date or timestamp and brief phase marker

## Freshness Standard

`MEMORY.md` is fresh enough when all of the following are true:

- the current objective still matches the active user request
- the active working set still names the files most likely to matter next
- completed subtasks are not still listed as pending
- decisions already made still match the current code and docs
- blockers and validation status reflect the latest meaningful attempt
- next steps are executable without re-reading large areas of the repo
- the file can be reread quickly, usually in under two minutes

Fresh enough does not mean perfect. It means good enough to prevent wasteful rescanning and scope drift.

## Update Triggers

Update `MEMORY.md` when:

- the objective changes materially
- stack, archetype, or manifest inference becomes clearer
- the working set changes materially
- a meaningful decision is made
- something is explicitly ruled out
- a major subtask finishes
- testing or smoke validation changes the task state
- the session is about to stop after meaningful progress
- a fresh session is likely to continue the same task soon

## When Not To Update

Do not update `MEMORY.md` for:

- tiny edits completed in one pass with no realistic continuation risk
- every inspected file when nothing important was learned
- every command run
- every passing test when the overall task state did not change
- speculative ideas that have not affected the plan

If a write would add noise rather than clarify the next move, skip it.

## Size And Signal

Keep `MEMORY.md` small and high-signal.

Practical target:

- usually 40 to 120 lines
- usually under about 1,500 words
- shorter for trivial tasks
- rewritten instead of endlessly appended when sections go stale

High-signal habits:

- use exact file paths
- prefer bullets over paragraphs
- record findings, not narration
- replace stale next steps instead of stacking old ones
- delete resolved blockers and irrelevant files
- move durable transition state into a handoff snapshot when a fixed checkpoint matters

## Rewrite Versus Append

Rewrite when:

- more than a third of the file is stale
- the task moved into a new phase
- the next working set is different from the previous one
- the old summary reads like a transcript

Append only when:

- the current phase is still active
- the new information is small
- the old sections remain accurate

The default should be prune and rewrite, not accumulate.

## Prompt-First Repo Rules

In prompt-first repos, `MEMORY.md` should also capture:

- the highest completed prompt filename
- the next intended prompt filename
- prompt numbering decisions already made
- any prompt files that were intentionally not created

Use exact filenames such as `.prompts/003-add-memory-layer.txt`, not vague labels like "the next refine prompt".

## Relationship To Handoff Snapshots

Use `MEMORY.md` for mutable current state.

Use a handoff snapshot for a durable point-in-time transfer when:

- the task will span sessions
- another assistant or human is likely to continue
- a derived repo needs an auditable transition artifact
- the current checkpoint includes meaningful completed work plus pending work

`MEMORY.md` may point to the latest handoff snapshot, but it should not become an archive of old checkpoints.
