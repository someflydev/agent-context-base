# Commit Hygiene

Commits should be easy to review, revert, and explain.

## Shape

- keep one coherent change per commit
- separate doctrine, router, manifest, example, and script changes when that separation improves reviewability
- avoid mixing unrelated cleanup into feature work

## Message Style

Prefer a bracketed repo-local prefix and an imperative summary.

Example:

`[BASE_04] add FastAPI and Hono stack packs`

Multi-line messages should explain:

- what changed
- why the batch belongs together
- any important boundary or follow-up note

## Review Standard

Before committing, confirm:

- filenames are deterministic
- cross-references resolve
- new guidance does not contradict doctrine
- tests or validation scripts were run when applicable

## Anti-Patterns

- giant "initial dump" commits with unrelated content
- renaming files without updating references
- sneaking behavior changes into documentation-only commits

