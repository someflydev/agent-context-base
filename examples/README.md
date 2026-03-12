# Examples

This directory contains the canonical implementation patterns for future repos derived from this base.

Examples are intentionally different from templates:

- examples show a preferred completed pattern
- templates provide a starter scaffold to specialize later

## Example Categories

- `canonical-api/`: route, handler, controller, and service-boundary examples
- `canonical-cli/`: command, flag, and output-shape examples
- `canonical-dokku/`: Dokku deployment wiring and release posture
- `canonical-integration-tests/`: real-infra tests against isolated `docker-compose.test.yml`
- `canonical-prompts/`: monotonic prompt-file layout and prompt text
- `canonical-rag/`: local indexing config and metadata shape
- `canonical-seed-data/`: deterministic seed data flows
- `canonical-smoke-tests/`: smallest meaningful happy-path checks
- `canonical-storage/`: database, cache, queue, search, and vector boundary patterns
- `canonical-workflows/`: compact workflow artifacts such as post-flight checklists

## Selection Rule

Pick the category closest to the active workflow, archetype, and stack. Prefer one direct example over a blended hybrid.

## Maintenance Rule

When doctrine, manifests, or first-class stack guidance changes, review the affected canonical example quickly. A stale example creates more confusion than no example.
