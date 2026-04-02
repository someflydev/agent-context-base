# Sessions

Session logs for meaningful work sessions that produced non-obvious findings.

**This directory is gitignored.** Files here are local-only and will not be committed.
Write session logs freely; promote durable findings to `memory/concepts/` when they
are stable enough to commit.

## What Belongs Here

- Session logs for substantial work sessions (not trivial one-file edits)
- Prompt execution notes when the execution produced unexpected results or detours
- Exploration results that should not be re-discovered by a future session
- Decision rationale too specific to be a reusable concept

## What Does NOT Belong Here

- Summaries of completed or paused prompts → `memory/summaries/`
- Durable recurring knowledge → `memory/concepts/`
- Live task state → `context/TASK.md`, `context/SESSION.md`
- General-purpose transfer snapshots → `artifacts/handoffs/`

## File Format Convention

Two accepted filename patterns:
- `YYYY-MM-DD-<slug>.md` — for date-anchored session logs
- `PROMPT_XX-session.md` — for notes tied to a specific prompt execution

Required sections:
```
# Session: <description>

Date: YYYY-MM-DD
Prompt Context: <prompt file or task description>

## Key Findings
## Decisions Made
## Open Questions
```

## Pruning Convention

Sessions older than ~30 days whose findings have been promoted to `concepts/` or
`summaries/` may be removed. Never prune a session that is the sole record of a decision
not captured elsewhere.

## Relationship To `artifacts/handoffs/`

`memory/sessions/` holds prompt-first session notes indexed by prompt or date.
`artifacts/handoffs/` holds general-purpose timestamped transfer snapshots. Both can
coexist — they serve different lookup patterns.
