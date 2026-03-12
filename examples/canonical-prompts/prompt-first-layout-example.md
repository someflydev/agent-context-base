# Prompt-First Layout Example

Use a dedicated prompt directory and keep numbering strictly monotonic.

Recommended layout:

```text
.prompts/
  001-bootstrap-repo.txt
  002-add-fastapi-smoke-test.txt
  003-refine-manifests.txt
```

Rules this example makes explicit:

- each prompt references exact repo paths
- each prompt has one dominant goal
- later prompts build on files created by earlier prompts
- numbering never resets or backfills old gaps

Related files:

- `examples/canonical-prompts/001-bootstrap-repo.txt`
- `examples/canonical-prompts/002-refine-test-surface.txt`

