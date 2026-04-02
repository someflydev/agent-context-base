# Summaries

Prompt-boundary compaction artifacts. The primary source for fresh sessions resuming a
specific prompt.

**This directory is gitignored.** Files here are local-only and will not be committed
automatically. `PROMPT_90_completion.md` is a committed format example (tracked before the
gitignore was added); new summary files remain local.

## What Belongs Here

- Prompt-boundary compaction artifacts written when pausing or completing a prompt
- Checkpoint summaries that capture the exact state at a meaningful boundary
- Resume handoffs that let a fresh session pick up without rediscovery

## Standard Filename Patterns

| Pattern                      | When to use                                     |
|------------------------------|-------------------------------------------------|
| `PROMPT_XX_completion.md`    | Written when a prompt is fully done             |
| `PROMPT_XX_resume.md`        | Written when a prompt is paused mid-execution   |

## Required Sections

```
## Objective
## Completed
## Remaining          (omit or mark "none" if fully done)
## Tests Status
## Files Touched
## Key Commits
## Pitfalls and Caveats
## Next Recommended Action
## Created At
```

## Relationship To `context/MEMORY.md`

Summaries are **immutable once written**. `context/MEMORY.md` is mutable live state.
After writing a summary, prune `context/MEMORY.md` to stay current rather than archival.
Do not write summaries that simply copy `MEMORY.md` content into a different filename —
summaries should represent a meaningful boundary artifact, not a backup.

## Quality Standard

- Use real data: real commit hashes, real file paths, real test output
- No placeholder text or `<TODO>` markers
- Pitfalls section must reflect actual friction encountered, not hypothetical risks
- See `PROMPT_90_completion.md` as the canonical format example
