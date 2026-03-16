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

## Redis Streams

### When to Use Redis Streams

Use Redis Streams (not a List or Pub/Sub) when:

- You need durable consumer groups — multiple named groups tracking independent offsets.
- You need at-least-once delivery — each message must be ACKed or it stays in the Pending Entries List (PEL).
- You need ordered delivery within the stream.
- Volume is within Redis's capacity (< 500k messages/day) and you do not need partition scaling.
- You already run Redis and don't want to introduce a separate broker service.

Do NOT use Redis Streams as a replacement for Kafka when:

- Volume requires horizontal partitioning beyond what a single Redis instance handles.
- Long-term message retention (days/weeks) is required — MAXLEN trims messages; there is no log file.
- Cross-team schema contracts need a registry.

### Key Commands

**XADD — append a message:**
```python
# redis-py: pip install redis
import redis
r = redis.Redis.from_url(os.getenv("REDIS_URL"))

msg_id = r.xadd(
    "domain:orders:events",
    {
        "payload_version": "1",
        "correlation_id": "req-001",
        "event_type": "order.created",
        "entity_id": "ord-9182",
        "tenant_id": "acme",
    },
    maxlen=10000,    # approximate trim — keeps stream bounded
    approximate=True,
)
# msg_id: b'1710000000000-0' (millisecond timestamp + sequence)
```

**XREADGROUP — consume with a consumer group:**
```python
# Create consumer group (idempotent with mkstream=True):
try:
    r.xgroup_create("domain:orders:events", "order-processors", id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise  # group already exists is OK

# Read new messages (> means "after my last-delivered ID"):
messages = r.xreadgroup(
    groupname="order-processors",
    consumername="worker-1",
    streams={"domain:orders:events": ">"},
    count=10,
    block=2000,   # block up to 2 seconds if no messages
)
for stream_name, entries in (messages or []):
    for msg_id, fields in entries:
        try:
            process_event(fields)
            r.xack("domain:orders:events", "order-processors", msg_id)
        except Exception as e:
            log.error(f"processing failed for {msg_id}: {e}")
            # Do NOT ack — message stays in PEL for retry or DLQ handling
```

**XPENDING — inspect unacknowledged messages:**
```python
# Summary: how many pending messages per consumer
pending_summary = r.xpending("domain:orders:events", "order-processors")

# Detail: list specific pending messages
pending_detail = r.xpending_range(
    "domain:orders:events", "order-processors",
    min="-", max="+", count=100
)
# Each entry: {message_id, consumer, time_since_delivered_ms, delivery_count}
```

**XCLAIM — reassign stale messages from a crashed consumer:**
```python
# Reassign messages idle for more than 30 seconds to "worker-2"
claimed = r.xclaim(
    "domain:orders:events",
    "order-processors",
    "worker-2",
    min_idle_time=30000,   # milliseconds
    message_ids=[stale_msg_id],
)
```

**XRANGE — replay from a given ID:**
```python
# Read all messages from a specific ID onwards:
messages = r.xrange("domain:orders:events", min="1710000000000-0", max="+")
```

### Stream Naming Convention

- Pattern: `{domain}:{entity}:{event_type}` (colon-separated, following Redis key convention)
- Examples: `domain:orders:events`, `notifications:emails:queued`
- Keep the stream name short — it appears in every XADD/XREADGROUP call.

### Trimming Strategy

- Use `MAXLEN ~ N` (approximate) on every XADD to bound stream size automatically.
- Approximate trimming (`approximate=True`) is significantly cheaper than exact trimming.
- Set MAXLEN based on retention window: if messages are typically consumed within 1 hour and throughput is 100/sec, `MAXLEN=360000` keeps a 1-hour window with margin.
- For audit or replay needs beyond the trim window, archive to a persistent store before trim.

### Local Dev docker-compose Note

No changes to the docker-compose pattern — Redis Streams use the same `redis:7-alpine` service as other Redis features. Ensure the service uses a named volume or `--save ""` based on whether stream persistence between restarts is needed in dev.

### Testing Expectations for Streams

- Prove a produce + consume round-trip with XACK.
- Prove that an unacknowledged message (no XACK) reappears in XPENDING.
- Prove XCLAIM correctly reassigns a stale message.
- Use a short `maxlen` in tests to verify trimming behavior.
- Run against a real Redis instance — do not mock XREADGROUP semantics.

### Related

- context/doctrine/broker-selection.md — when Redis Streams vs NATS vs Kafka
- context/stacks/nats-jetstream.md
- context/stacks/kafka.md

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
