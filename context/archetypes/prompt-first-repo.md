# Prompt-First Repo

Use this archetype when the repository itself exists to coordinate prompts, routing, manifests, examples, templates, and bootstrap guidance.

## Common Goals

- make task routing obvious
- keep context loading small
- separate doctrine from workflows and examples
- support future descendant repos cleanly

## Required Context

- `context/doctrine/prompt-first-conventions.md`
- `context/doctrine/context-loading-rules.md`
- `context/stacks/prompt-first-repo.md`

## Common Workflows

- `context/workflows/bootstrap-repo.md`
- `context/workflows/generate-prompt-sequence.md`
- `context/workflows/post-flight-refinement.md`

## Likely Examples

- `examples/canonical-prompts/README.md`
- `examples/README.md`

## Typical Anti-Patterns

- giant router files
- blurred boundaries between examples and templates
- prompt naming that is not monotonic or explicit

