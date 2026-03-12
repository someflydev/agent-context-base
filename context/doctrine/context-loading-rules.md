# Context Loading Rules

Load less context first. Expand only when the task requires it.

## Preferred Load Order

1. `README.md`
2. one router file
3. only the doctrine files relevant to the task
4. one workflow
5. one archetype if project shape matters
6. required stack files
7. one preferred canonical example
8. a template only if scaffolding is needed

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

