# Examples

This directory contains the canonical implementation patterns for future repos derived from this base.

Doctrine and workflows are the generic layer. Examples are the preferred completed implementation layer.

Examples are intentionally different from templates:

- examples show a preferred completed pattern
- examples should be real code or real runnable assets when they claim a stack-specific implementation
- templates provide a starter scaffold to specialize later

## Example Categories

- `canonical-api/`: route, handler, controller, and service-boundary examples
- `canonical-cli/`: command, flag, and output-shape examples
- `canonical-data-acquisition/`: source research, acquisition invariants, stack-selection guidance, raw archival, parser, classification, sync, and event examples
- `canonical-dokku/`: Dokku deployment wiring and release posture
- `canonical-integration-tests/`: real-infra tests against isolated `docker-compose.test.yml`, including Playwright guidance for backend-driven UI verification
- `canonical-observability/`: logs, metrics, and trace-shape examples
- `canonical-prompts/`: monotonic prompt-file layout and prompt text
- `canonical-rag/`: local indexing config and metadata shape
- `canonical-seed-data/`: deterministic seed data flows
- `canonical-smoke-tests/`: smallest meaningful happy-path checks
- `canonical-storage/`: database, cache, queue, search, and vector boundary patterns
- `canonical-workflows/`: compact workflow artifacts such as post-flight checklists
- `fixtures/`: minimal fixture datasets that stay intentionally small

## Selection Rule

Pick the category closest to the active workflow, archetype, and stack. Prefer one direct example over a blended hybrid.
When several examples are relevant, prefer the closest stack match with the highest honest verification level.
If a stack-specific canonical example does not exist yet, say so and fall back to the invariant docs plus the nearest verified example.

## Maintenance Rule

When doctrine, manifests, or first-class stack guidance changes, review the affected canonical example quickly. A stale example creates more confusion than no example.

Use `examples/catalog.json` when the matching example is not obvious from memory.
Use `verification/example_registry.yaml` when trust level, confidence, or harness coverage matters.

The data-acquisition category now includes real source-sync examples for Dart, Clojure, Scala, Kotlin, Ruby, OCaml, Elixir, Nim, Zig, and Crystal in addition to the earlier Python, Go, Rust, and TypeScript anchors. Verification depth still varies by stack and should be read from the registry, not inferred from file presence.
