# Memory Continuity Discipline

Use this skill when reading or writing `MEMORY.md` to maintain useful continuity without stale state.

For templates and format rules, see `context/memory/`.

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

## Good Triggers

- "how to read MEMORY.md"
- "is this MEMORY.md stale"
- "what to write in MEMORY.md"
- "update the continuity file"
- "memory is out of date"
- "how should I update the memory file"

## Avoid

- using a stale `MEMORY.md` to drive task scope without first validating it against current repo state
- writing details that are already in the code or git history
- updating `MEMORY.md` after every small step rather than at phase boundaries
- letting a completed objective in `MEMORY.md` block a new task
