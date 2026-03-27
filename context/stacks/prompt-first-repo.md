# Prompt-First Repo

Use this pack when the repo itself is organized around prompts, routing docs, manifests, examples, and bootstrap-friendly structure.

This pack also governs descendant repo generation now that all generated repos keep a visible `.prompts/` sequence and hidden generator-owned state under `.acb/`.

## Typical Repo Surface

- `AGENT.md`
- `CLAUDE.md`
- `.prompts/`
- `.acb/`
- `context/`
- `manifests/`
- `examples/`
- `templates/`
- prompt directories in descendant repos

## Change Surfaces To Watch

- routing clarity
- prompt numbering discipline
- cross-reference accuracy
- boundaries between doctrine, workflows, examples, and templates

## Testing Expectations

- validate file presence and manifest structure
- preview context bundles to confirm routing order
- add smoke checks for scripts that future repos will depend on

## Common Assistant Mistakes

- turning routers into philosophy dumps
- adding duplicate guidance in multiple layers
- introducing prompt filenames that are not monotonic or not explicit
