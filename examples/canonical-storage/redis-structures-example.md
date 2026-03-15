# Redis Data Structures Example

Redis provides named structures, not just a key-value store. Picking the right structure reduces memory
overhead, enables atomic operations, and prevents expiry from silently stomping live state.

## Rule of Thumb

Reach for a Redis structure when:

- the access pattern is a scan, rank, or count — sorted set
- the value is small, compound, and partially updated — hash
- the lifetime is bounded and the value is single-valued — string with TTL
- the consumer reads in insertion order and tolerates redelivery — stream

Do not serialize everything into a JSON blob under a string key. JSON blobs break atomic field updates
and hide access-pattern intent from both the application and observability tooling.

## Key Naming Convention

Use a colon-delimited namespace so flush and scan operations stay scoped:

```text
<env>:<domain>:<identifier>
```

Examples:

```text
dev:leaderboard:weekly-signups
test:session:user:42
prod:rate-limit:tenant:acme
```

Always prefix test keys with `test:` so integration test teardown never touches dev or prod data.

## Sorted Set: Leaderboard

```text
ZADD dev:leaderboard:weekly-signups 147 "acme"
ZADD dev:leaderboard:weekly-signups 88  "globex"
ZADD dev:leaderboard:weekly-signups 203 "initech"
ZREVRANGE dev:leaderboard:weekly-signups 0 9 WITHSCORES
```

Why sorted set: the score is the metric (signups, views, revenue). `ZADD` is idempotent per member.
`ZREVRANGE` returns top-N in O(log N + M). Replacing this with a sorted list of JSON blobs would
require a read-modify-write on every update.

Update an existing score by increment rather than by overwrite:

```text
ZINCRBY dev:leaderboard:weekly-signups 12 "acme"
```

## String with TTL: Session or Cache Key

```text
SET dev:session:user:42 '{"user_id":42,"tenant":"acme","role":"analyst"}' EX 3600
```

Why string with TTL: the entire value is either valid or expired. There is no need to update individual
fields. `EX 3600` sets a one-hour expiry atomically. If the session is refreshed, overwrite the key
with a new TTL.

For rate-limiting, increment a counter and set expiry only on first creation:

```text
SET dev:rate-limit:tenant:acme 0 EX 60 NX
INCR dev:rate-limit:tenant:acme
```

This is atomic: `SET ... NX` initialises the key only if it does not already exist. Subsequent `INCR`
calls never reset the expiry.

## Hash: Small State Record

```text
HSET dev:report-run:acme:daily-signups \
  status "running" \
  started_at "2026-03-10T14:00:00Z" \
  payload_version "2" \
  row_count ""
```

Why hash: the record has named fields that are updated individually. `HSET` allows partial updates
without reading and reserializing the full document. `HGETALL` retrieves the full record cheaply.

Read a single field without loading the full record:

```text
HGET dev:report-run:acme:daily-signups status
```

Update only the fields that changed on completion:

```text
HSET dev:report-run:acme:daily-signups \
  status "ready" \
  finished_at "2026-03-10T14:00:42Z" \
  row_count "84"
```

## Stream: Ordered Append Log

```text
XADD dev:events:report-completed * \
  tenant_id acme \
  report_id daily-signups \
  row_count 84 \
  completed_at "2026-03-10T14:00:42Z"
```

Why stream: consumers read in insertion order, can read from an offset, and a consumer group allows
multiple workers to claim entries without duplication. Unlike a list-based queue, stream entries are
not destroyed on read unless explicitly acknowledged.

Read the most recent 10 entries:

```text
XREVRANGE dev:events:report-completed + - COUNT 10
```

Read from a stored consumer group cursor:

```text
XREADGROUP GROUP report-consumers worker-1 COUNT 5 STREAMS dev:events:report-completed >
```

Acknowledge after successful processing:

```text
XACK dev:events:report-completed report-consumers <entry-id>
```

## What Not To Do

Avoid:

```text
SET dev:report-run:acme:daily-signups '{"status":"running","started_at":"...","row_count":0}'
```

Reasons to avoid:

- updating `row_count` alone requires a read-deserialize-mutate-reserialize-write cycle
- there is no native increment for a field inside a JSON blob
- TTL silently expires the whole blob when you only wanted a timeout on one field
- the blob gives no access-pattern signal to observability tooling

## Expiry Discipline

Set expiry at the right granularity:

- session key — full TTL on the string, refresh on activity
- rate-limit counter — TTL on the window (e.g. 60 seconds), reset with `SET ... NX`
- hash state record — no TTL unless the record has a known lifecycle end; use explicit deletion instead
- stream — use `MAXLEN` trimming on `XADD` rather than key expiry if the stream is append-only

## Verification Level

Structure-verified (file existence and marker checks only). No live Redis instance is wired in the
default verification tier.

## When To Use This Example vs. `redis-mongo-shape-example.md`

Use this example when:

- you are building a Redis-only workload
- the design question is which Redis structure to use and why

Use `redis-mongo-shape-example.md` when:

- the design combines Redis and MongoDB in a single repo
- you need the combined key-prefix and collection-naming convention in one place
