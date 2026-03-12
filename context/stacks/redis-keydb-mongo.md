# Redis / KeyDB / MongoDB

Use this pack when a repo adds cache, document-store, or simple queue-adjacent behavior through Redis, KeyDB, or MongoDB.

## Typical Repo Surface

- storage client setup
- environment configuration
- repository or adapter layer
- test fixtures and seed data
- Compose service definitions

## Change Surfaces To Watch

- key naming
- TTL behavior
- collection naming and indexes
- serialization shape
- seed and reset commands

## Testing Expectations

- use Docker-backed isolated test instances
- prove one real write plus one real read
- add an edge case around missing keys, TTL expiry assumptions, or collection shape if relevant

## Common Assistant Mistakes

- using one shared local instance for dev and test
- skipping cleanup boundaries
- assuming cache and persistence changes can be validated with mocks alone

