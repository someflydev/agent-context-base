# Event Streaming Patterns

Use this pack when source sync stages are coordinated through durable events, subjects, or queues.

## Typical Repo Surface

- scheduler or trigger publisher
- fetch requested and completed events
- parse and classification consumers
- dead-letter or terminal-failure handling
- source health and replay tooling

## Change Surfaces To Watch

- event subject naming
- idempotency key shape
- duplicate delivery handling
- checkpoint movement after consumer success
- payload size and reference strategy

## Testing Expectations

- verify one event-driven happy path end to end
- test duplicate delivery or replay-safe consumption
- keep large raw payload bodies out of event messages; pass references instead

## Common Assistant Mistakes

- publishing framework-centric event names instead of sync-stage names
- putting raw documents directly on the bus
- assuming ordered delivery across unrelated sources
