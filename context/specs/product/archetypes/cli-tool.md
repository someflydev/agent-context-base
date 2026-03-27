---
acb_origin: canonical
acb_source_path: context/specs/product/archetypes/cli-tool.md
acb_role: product
acb_archetypes: [cli-tool]
acb_version: 1
---

## CLI Tool Intent

The product surface is an operator-facing command line. Commands, flags, output shape, and failure behavior are part of the product spec and must remain explicit.

The repo should optimize for repeatable local use, readable help text, and deterministic command behavior rather than hidden workflow magic.
