# Context Loading And Anti-Sprawl Rules

Purpose: minimize unnecessary reading.

Rules:

- Start from the repo profile manifest.
- Load only the doctrine files that govern the task.
- Load one workflow before loading stacks.
- Load only the active stack packs.
- Consult canonical examples before inventing.
- Escalate only when a stop condition is hit.

Prevents:

- scanning the entire repo
- context-window waste
- invented conventions
