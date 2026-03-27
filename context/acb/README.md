# ACB Payload Rules

This directory contains the machine-readable selection rules that drive spec-driven development and validation-driven autonomy payloads for generated repos.

`profile-rules.json` is the canonical composition map. It explains:

- which doctrines and routers are active by default
- which capabilities are implied by each archetype
- which support services imply storage or eventing concerns
- which validation gates should be surfaced for archetypes, stacks, and capabilities

The canonical narrative modules live beside this file under:

- `context/specs/`
- `context/validation/`

Generated repos should not copy this directory directly. Instead, the payload composer uses it to build a concise repo-local `.acb/` bundle with synthesized specs, validation plans, and machine-readable indexes.
