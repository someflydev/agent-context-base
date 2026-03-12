# Context Loading Rules

Load less context first. Expand only when the task requires it.

## Preferred Load Order

1. `README.md`
2. one router file
3. one anchor if the task benefits from a compact reminder
4. only the doctrine files relevant to the task
5. one workflow
6. one archetype if project shape matters
7. required stack files
8. one preferred canonical example
9. a template only if scaffolding is needed

## Escalation Triggers

Load more context when:

- the task spans more than one storage or service boundary
- the task is blocked on stack-specific structure
- deployment behavior matters
- examples disagree or are missing

## Context To Avoid Loading Blindly

- all doctrine files at once
- all manifests at once
- all examples at once
- all stack docs for unrelated ecosystems

## Practical Rule

If you cannot explain why a file is being loaded for the current task, do not load it yet.

When ambiguity persists, stop and use `context/doctrine/stop-conditions.md` instead of loading more files blindly.
