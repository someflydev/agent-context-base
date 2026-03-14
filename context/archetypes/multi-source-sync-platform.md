# Multi-Source Sync Platform

Use this archetype when the repo coordinates recurring acquisition from multiple sources, often with events, persistence, and downstream API or UI exposure.

## Common Goals

- multiple independent source adapters
- per-source checkpoints and health state
- event-driven or queue-backed coordination
- recurring sync orchestration
- idempotent persistence and replay

## Required Context

- `context/doctrine/data-acquisition-philosophy.md`
- `context/doctrine/sync-safety-rate-limits.md`
- `context/doctrine/source-research-discipline.md`

## Common Workflows

- `context/workflows/research-data-sources.md`
- `context/workflows/add-recurring-sync.md`
- `context/workflows/add-event-driven-sync.md`
- `context/workflows/add-source-backoff-retry.md`

## Likely Examples

- `examples/canonical-data-acquisition/README.md`
- `examples/canonical-observability/README.md`

## Typical Anti-Patterns

- one scheduler job doing all fetch and parse work inline
- shared retry state across unrelated sources
- event contracts that hide which source or sync window they refer to
