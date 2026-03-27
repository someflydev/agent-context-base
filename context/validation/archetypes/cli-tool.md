---
acb_origin: canonical
acb_source_path: context/validation/archetypes/cli-tool.md
acb_role: validation
acb_archetypes: [cli-tool]
acb_version: 1
---

## CLI Validation

Validate `--help`, one valid command, and one invalid invocation with explicit exit-code and output expectations.

Capture stdout or stderr explicitly. CLI validation is incomplete if exit codes pass but operator-facing text shape is unknown.
