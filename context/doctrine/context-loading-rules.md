# Context Loading Rules

Load less context first. Expand only when the task requires it.

## Preferred Load Order

1. `AGENT.md` or `CLAUDE.md`
2. `manifests/project-profile.yaml` or the closest manifest
3. `README.md` only if it exists and is clearly maintained
4. one router file
5. one anchor if the task benefits from a compact reminder
6. only the doctrine files relevant to the task
7. one workflow
8. one archetype if project shape matters
9. required stack files
10. one preferred canonical example
11. a template only if scaffolding is needed

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
