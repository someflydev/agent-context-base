# Repo Signal Detection

Use this skill to infer stack and archetype from the repository itself.

## Strong Signals

- lockfiles and package manifests
- framework-specific entrypoints
- migration directories
- Compose files
- test directory structure
- deployment artifacts such as `Procfile`

## Weak Signals

- one-off comments
- old example names
- speculative docs not connected to active files

## Procedure

1. inspect root manifests and lockfiles
2. inspect dominant source directories
3. inspect test and infra directories
4. map findings through `context/router/stack-router.md` and `context/router/archetype-router.md`

## Avoid

- choosing a stack from one transient script
- assuming a future-supported stack is already active

