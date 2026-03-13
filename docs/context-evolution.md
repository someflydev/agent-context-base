# Context Evolution

This changelog records durable architectural changes to the base itself.

## 2026-03-13: Documentation Refactor

- rewrote the root README as the front-facing entrypoint
- reduced `AGENT.md` and `CLAUDE.md` to fast boot docs
- compressed overlapping docs into a smaller architecture and usage hierarchy
- simplified the visual model to a few diagrams that match the actual runtime, generation, verification, and multi-agent patterns
- aligned the generated-repo templates with the new boot guidance

## 2026-03-12: Reliability And Operations Pass

- added assistant anchors under `context/anchors/`
- added context weighting, repo-signal hints, and example ranking metadata
- added broader context validation and prompt-first repo analysis tooling
- tightened Compose naming, port allocation, and environment-isolation checks

## Earlier Milestones

- v2 introduced manifests, canonical example files, templates, and `scripts/new_repo.py`
- v1 established the split between doctrine, workflows, stacks, archetypes, and routers
