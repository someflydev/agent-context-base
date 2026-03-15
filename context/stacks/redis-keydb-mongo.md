# Redis / KeyDB / MongoDB — Mixed Storage

Use this pack when a repo deliberately combines Redis (or KeyDB) with MongoDB in one service — for example, a cache layer backed by a document store, queue-adjacent coordination backed by persistent documents, or a migration or comparison decision between similar storage layers.

If you are implementing Redis or MongoDB alone, load the solo packs instead:

- Redis only → `context/stacks/redis.md`
- MongoDB only → `context/stacks/mongo.md`

KeyDB is a Redis-compatible drop-in. Treat it as Redis in implementation guidance unless the task explicitly involves KeyDB-specific behavior.

## When To Use This Pack Over The Solo Packs

- The repo uses Redis and MongoDB together and the interaction between them is a design concern
- The task involves deciding between Redis and MongoDB (or Redis and KeyDB) for a specific use case
- The service has a cache-plus-document-store pattern where both sides are changing together
- The task involves migrating or replacing one storage layer with another in the same service

## Typical Repo Surface

- Redis client setup alongside a MongoDB client setup in the same service
- Separate environment variables and Docker services for each backing store
- Repositories or adapters that read from one store and write to the other
- `docker-compose.yml` / `docker-compose.test.yml` — both `redis` and `mongo` services with separate isolated volumes for dev and test

## Change Surfaces To Watch

- Key naming (Redis) and collection naming (MongoDB) — keep both explicit and documented in constants
- TTL behavior (Redis) and retention strategy (MongoDB) — both need explicit policies; do not leave either unbounded
- Serialization shape — if the same data moves between Redis and MongoDB, document the transform at the boundary
- Seed and reset commands must cover both services
- Port isolation — dev and test must use separate ports for both services

## Testing Expectations

- Use Docker-backed isolated instances for both Redis and MongoDB
- Prove at least one real write-plus-read for each backing store within the integration test boundary
- Test the interaction between the two stores if the design depends on one informing the other (e.g., cache miss falls through to document store)
- Do not share dev and test instances for either service

## Common Assistant Mistakes

- Reaching for this pack when the repo only uses one of these technologies — use the solo pack instead
- Skipping cleanup boundaries between test runs when two services are both in play
- Assuming cache and persistence changes can be validated with mocks alone
- Conflating KeyDB and Redis without noting where behavior diverges in the specific version in use
