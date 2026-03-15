# Redis

Use this pack when a repo uses Redis as its primary in-memory data store. Redis is the right choice for expiring keys, counters, leaderboards, rate limiting, coordination primitives, and lightweight streaming. It is not a general-purpose document store or a replacement for a relational database.

Poor fit: durable storage where data must survive a Redis restart without an explicit persistence strategy, complex document queries, or relational joins.

## Typical Repo Surface

- `app/cache/*.py` or `app/redis/*.py` — Redis client setup and operation wrappers
- `app/services/*.py` — service logic that reads or writes Redis state
- `docker-compose.yml` / `docker-compose.test.yml` — `redis` service with named volumes or `--save ""` for ephemeral test instances
- `.env` / `.env.test` — `REDIS_URL` pointing to separate dev and test instances

## Data Structure Selection

Choose the right native structure for the job. Do not serialize everything into strings.

| Structure    | Use when                                                                 |
|--------------|--------------------------------------------------------------------------|
| String + TTL | Simple cache entries, tokens, single values with expiry                  |
| Hash         | Record-like objects with multiple named fields (user session, config)    |
| Set          | Membership checks, unique tag sets, deduplication                        |
| Sorted set   | Leaderboards, priority queues, time-windowed rank queries                |
| List         | Job queues, append-only event logs, bounded recent-items lists           |
| Stream       | Durable append log with consumer groups, event fan-out, at-least-once   |

## Change Surfaces To Watch

- **Key naming**: use a consistent prefix scheme (`service:entity:id`). Undocumented keys drift into naming collisions across services or environments.
- **TTL discipline**: every cache key that can grow unboundedly must carry a TTL. Audit new key patterns for missing expiry.
- **Serialization format**: if you serialize structs into strings, document the format. Changing it without a migration strategy corrupts live data.
- **Eviction policy**: confirm `maxmemory-policy` is appropriate. `allkeys-lru` for a pure cache; `noeviction` for coordination primitives where dropped keys cause correctness failures.
- **Persistence mode**: `RDB`, `AOF`, or none — be explicit. Test instances should typically use `--save ""` (no persistence) to avoid cross-test contamination.

## Testing Expectations

- Run integration tests against a real isolated Redis instance (Docker-backed, separate port from dev)
- Prove one write and one retrieval for each data structure being introduced
- For TTL-sensitive logic, use short TTLs in tests or verify expiry behavior explicitly — do not mock expiry
- For sorted set or leaderboard logic, prove rank correctness with at least three entries
- For stream or list consumers, prove that a message is enqueued and consumed within the test boundary
- Do not share the Redis instance between dev and test — cross-test contamination is hard to debug

## Credible Use Cases

- **Leaderboard**: sorted set with score as a numeric rank metric; `ZREVRANGE` or `ZREVRANGEBYSCORE` for top-N retrieval
- **Expiring cache**: string key with `SET key value EX ttl` — simple and correct for single-value caching
- **Counter / rate limit**: `INCR` with `EXPIRE`; use a Lua script or pipeline for atomic check-and-increment
- **Distributed lock / coordination**: `SET key value NX EX ttl` pattern; always include a TTL to prevent lock starvation
- **Lightweight job queue**: list with `RPUSH` / `BLPOP`; upgrade to a stream if you need consumer groups or replay
- **Event stream**: stream with `XADD` / `XREADGROUP`; appropriate when fan-out or at-least-once delivery matters

## Redis Modules

Optional capability expansion — do not assume presence without confirmation:

- **RedisJSON**: native JSON document storage with path-based queries
- **RedisBloom**: probabilistic data structures (bloom filter, count-min sketch)
- **RedisTimeSeries**: time-series data with downsampling and retention rules

Base Redis does not include these. Confirm module availability before designing around module-specific commands.

## Common Assistant Mistakes

- Flattening structured data into a single serialized JSON string when a hash, sorted set, or list would be more queryable and less fragile
- Missing TTL on cache keys that accumulate indefinitely
- Using the same Redis instance for dev and test environments
- Assuming Redis modules are available without confirming — do not use `JSON.SET` or `TS.ADD` unless the module is confirmed present
- Using `KEYS *` in any non-trivial environment — use `SCAN` with a cursor instead
- Not documenting the key namespace scheme, leading to collisions across services or deployments
