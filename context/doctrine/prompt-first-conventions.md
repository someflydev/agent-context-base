# Prompt-First Conventions

Prompt-first work should be structured, traceable, and easy to continue later.

## Monotonic Prompt Numbering

When a repo stores prompt files, use strictly monotonic numbering:

- `001-...`
- `002-...`
- `003-...`

Do not renumber old prompts. Do not reuse gaps. If `004` is skipped accidentally, the next prompt is still `005`.

## Explicit Filename References

Prompts should refer to exact repo paths when asking for changes.

Good:

- `Update templates/manifest/manifest.template.yaml`
- `Add tests under tests/integration/test_search_indexing.py`

Bad:

- "fix the manifest template"
- "update the search tests somewhere"

## Prompt Sequence Design

- each prompt should have one dominant goal
- later prompts should build on actual repo state, not assumed state
- prompts should reference previous output by filename when relevant

## Assistant Behavior

Assistants should infer tasks from natural language, but prompt files should still be explicit enough to reduce ambiguity during long-running work.

