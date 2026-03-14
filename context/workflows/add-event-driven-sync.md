# Add Event-Driven Sync

## Purpose

Coordinate source sync stages through durable events instead of implicit in-process chaining.

## When To Use It

- multiple sources or stages need loose coordination
- fetch, parse, classify, and persist should scale or retry independently

## Inputs

- event subjects or topics
- producer and consumer boundaries
- idempotency key strategy

## Sequence

1. define event names around domain stages, not framework internals
2. publish small events that reference source, run, window, and raw artifact or cursor metadata
3. make consumers idempotent before increasing concurrency
4. separate scheduling events from heavy processing events
5. record dead-letter or terminal-failure behavior explicitly
6. verify one end-to-end happy path and one duplicate-delivery path

## Outputs

- event contract
- producer and consumer boundaries
- retry-safe sync coordination

## Related Doctrine

- `context/doctrine/sync-safety-rate-limits.md`
- `context/doctrine/data-acquisition-philosophy.md`

## Common Pitfalls

- publishing huge payload bodies instead of references
- mixing consumer retry semantics with source retry semantics
- letting the UI depend directly on event arrival order

## Stop Conditions

- consumers cannot tolerate duplicate delivery
- event names do not tell operators which sync stage failed
- failure handling still depends on manual log reading alone
