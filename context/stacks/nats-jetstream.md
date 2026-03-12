# NATS JetStream

Use this pack when the repo adds durable messaging or stream-backed event flow.

## Typical Repo Surface

- connection bootstrap
- stream or consumer setup
- publisher code
- handler or consumer code
- smoke and integration tests

## Change Surfaces To Watch

- stream names
- subject naming
- consumer durability
- ack and retry behavior

## Testing Expectations

- smoke test the app path that depends on the connection only if it is a primary path
- integration test real publish and consume flow against an isolated test broker
- add at least one edge case around duplicate or retry-safe handling when behavior depends on it

## Common Assistant Mistakes

- treating JetStream like an in-memory queue
- hiding subject names in unclear helper layers
- skipping real broker tests for consumer behavior

