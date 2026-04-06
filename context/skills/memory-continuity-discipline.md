# Memory Continuity Discipline

Use this skill when reading or writing `MEMORY.md` to maintain useful continuity without stale state.

For templates and format rules, see `context/memory/`.

## Continuity Layers

Use the right continuity artifact for the right job.

- `memory/INDEX.md` is the committed orientation layer for the 3-tier memory base
- `memory/summaries/` is the primary resumption layer for prompt-first work
- `memory/concepts/` is the committed durable-knowledge layer for findings that survive multiple sessions
- `context/MEMORY.md` is local live runtime state for the current repo, not a committed prompt handoff
- `artifacts/handoffs/` is for general-purpose committed snapshots when the handoff is broader than one prompt

Preferred read order when resuming prompt-first work:

1. `memory/summaries/PROMPT_XX_resume.md` or `memory/summaries/PROMPT_XX_completion.md`
2. `memory/INDEX.md` for tier orientation when needed
3. `memory/concepts/` only for durable domain knowledge relevant to the task
4. `context/MEMORY.md` only when live repo-local state matters for the current session

## When To Create Each Artifact

Create continuity artifacts in this order:

1. write a prompt-boundary summary in `memory/summaries/` when pausing or completing a prompt
2. update `context/MEMORY.md` only when the repo's live local state changed in a way the next session must see
3. promote a finding to `memory/concepts/` only after it has become durable, reusable, and worth committing
4. create `artifacts/handoffs/` when the transfer needs a broader committed snapshot than a prompt summary provides

## Reading MEMORY.md

1. check whether the stated objective still matches current repo signals and the task in hand
2. check the working set: do the listed files still exist and look active?
3. check verification status: is the claimed verification state consistent with the test files present?
4. if any of these checks fail — objective completed, working set gone, or state contradicts current reality — treat `MEMORY.md` as outdated and do not let it constrain the current task
5. use only the parts that are still consistent

## Writing MEMORY.md

1. capture: current objective, active working set (3–7 files max), key decisions made, verification status (what was run, what passed), and the next concrete step
2. prune: completed sub-tasks, superseded plans, and files no longer on the change surface
3. update at meaningful stop points — when a phase boundary is crossed or a verification step completes, not continuously
4. never write implementation details already captured in the code or commit history — `MEMORY.md` is operational state, not a second source of truth

## Summary Discipline

For prompt-first work, `memory/summaries/` is the default handoff surface.

- write `PROMPT_XX_resume.md` when a prompt pauses mid-session
- write `PROMPT_XX_completion.md` when a prompt finishes and the next session should not rediscover what changed
- keep summaries concrete: changed files, decisions, verification state, and the next safe step
- do not use `context/MEMORY.md` as a substitute for prompt-boundary summaries

## Good Triggers

- "how to read MEMORY.md"
- "is this MEMORY.md stale"
- "what to write in MEMORY.md"
- "update the continuity file"
- "memory is out of date"
- "how should I update the memory file"
- "where should this handoff live"
- "do I need a resume summary or a concept file"

## Avoid

- using a stale `MEMORY.md` to drive task scope without first validating it against current repo state
- writing details that are already in the code or git history
- updating `MEMORY.md` after every small step rather than at phase boundaries
- letting a completed objective in `MEMORY.md` block a new task
- skipping `memory/summaries/` and expecting the next prompt session to rediscover the exact stopping point
