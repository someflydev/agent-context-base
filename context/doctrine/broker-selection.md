# Broker Selection

This is the first place to look when deciding which message broker to use for a new event-driven system. It covers NATS JetStream, Kafka, and Redis Streams. The answer here is opinionated — pick the one that fits, not the one with the longest feature list.

## Quick Decision Table

| Criterion | NATS JetStream | Kafka | Redis Streams |
|---|---|---|---|
| Operational complexity | Single binary (`nats-server -js`) | Broker + KRaft (or ZooKeeper, deprecated) | Redis instance (already running) |
| Throughput target | < 1M messages/day | > 1M messages/day, partition scaling | < 500k messages/day |
| Schema enforcement | None built-in | Schema registry (Avro, Protobuf, JSON Schema) | None built-in |
| Ordering guarantee | Per-subject | Per-partition | Per-stream |
| Consumer model | Push or durable pull | Consumer groups (partition-distributed) | Consumer groups (stream-wide) |
| Retention model | Configurable age/size/count | Configurable age/size/count | MAXLEN trim or XDEL (no log file) |
| At-least-once delivery | Yes — explicit ACK per message | Yes — manual offset commit | Yes — XACK after processing |
| Cross-team schema contracts | JSON convention only | Avro or Protobuf + registry | JSON convention only |
| Replay capability | Sequence-based replay from any stored message | Offset reset to any stored offset | XRANGE from any message ID |
| When to reach for it | Intra-cluster bus, single binary, NATS already present | High volume, JVM producer, cross-team schema contracts | Job queue on existing Redis, no separate broker |

## NATS JetStream

Reach for NATS JetStream when:

- Single-team or intra-service event bus with moderate volume (< 1M messages/day).
- Simple subject-based routing is sufficient; no schema registry needed.
- Local dev must be fast to spin up — single binary, no ZooKeeper, no external deps.
- The repo already uses NATS for pub-sub and needs persistence added.
- Fan-out to multiple consumers on different subjects with wildcard routing.
- At-least-once delivery with durable pull consumers is the requirement.

Do NOT use NATS JetStream when:

- Multiple teams need strict schema compatibility guarantees — use Kafka + schema registry.
- Kafka client libraries are already in use by consuming services.
- Partition-level throughput scaling is required — NATS scales vertically, not via partitions.
- Long-term (days/weeks) log retention for audit or replay at scale.

Key operational notes:

- Single binary deployment: `nats-server -js`
- Subject namespace is flat; streams bind to subject patterns.
- Consumer types: push (server delivers) or pull (client fetches in batches).
- Preferred consumer type in this repo: durable pull consumers — see `context/stacks/nats-jetstream.md`.
- docker-compose: `nats:2.10-alpine` with `-js` flag; healthcheck via HTTP monitoring port 8222.

## Kafka

Reach for Kafka when:

- Multiple independent consumer groups need to read the same topic at different offsets.
- Cross-team schema contracts require Avro or Protobuf with a schema registry.
- Message volume benefits from horizontal partition scaling (> 1M messages/day).
- Long-term retention (days to weeks) needed for replay, audit, or compliance.
- The primary producer is Clojure (jackdaw/Kafka Streams), Scala (Akka Streams/Spark), or a JVM-native pipeline.

Do NOT use Kafka when:

- Small-to-medium volume single-team service — NATS is simpler to operate.
- In-process or intra-service event bus — consider Redis Streams or NATS.
- Schema registry adds friction the team isn't ready to maintain.
- Local dev speed matters more than production fidelity (KRaft adds startup time).

Key operational notes:

- Modern local dev: `bitnami/kafka:3.7` with KRaft (no ZooKeeper).
- Production: KRaft mode is stable in Kafka 3.3+; ZooKeeper mode is deprecated.
- Consumer group semantics: partitions are distributed among group members; one partition per consumer at a time; scale consumers up to the partition count.
- Offset commit: always use manual commit (`enable.auto.commit=false`) for at-least-once.
- docker-compose: bitnami/kafka with KRaft config; healthcheck via `kafka-topics.sh`.

## Redis Streams

Reach for Redis Streams when:

- The repo already uses Redis for caching, rate limiting, or other state.
- Lightweight append log with consumer groups without a separate broker service.
- Volume is modest (< 500k messages/day).
- Messages can be trimmed after processing (no long-term retention needed).
- Fan-out to multiple consumer groups from a single stream is required.
- Task queue or job dispatch where Redis is the natural home.

Do NOT use Redis Streams when:

- Durable long-term retention is required — Redis Streams trim via MAXLEN or XDEL; data is not backed by a log file.
- Multiple independent teams or services need a strict schema contract.
- Volume requires horizontal partition scaling — Redis Streams do not partition.
- The broker concern is large enough to warrant a dedicated message broker deployment.

Key operational notes:

- Redis Streams commands: `XADD`, `XREAD`, `XREADGROUP`, `XACK`, `XPENDING`, `XRANGE`, `XCLAIM`.
- Consumer groups: created with `XGROUP CREATE`; each group tracks its own last-delivered ID.
- ACK semantics: after processing, `XACK` marks the message as acknowledged within the group.
- Pending entries: unacknowledged messages tracked in the Pending Entries List (PEL); use `XPENDING` to inspect; `XCLAIM` to reassign stale messages.
- Trimming: use `MAXLEN ~ N` (approximate) on `XADD` or standalone `XTRIM` to bound stream size.
- docker-compose: `redis:7-alpine`; healthcheck via `redis-cli ping`.

## Migration Paths

**If you outgrow NATS JetStream → Kafka:**
- The event schema doesn't need to change (keep `payload_version`, `correlation_id`, etc.).
- Replace the NATS connection/publish call with a Kafka producer.
- Replace the NATS subscription with a Kafka consumer group.
- Add a schema registry step if cross-team contracts are now needed.
- Run both in parallel during migration: new consumers read from Kafka, old from NATS, until all consumers are migrated.

**If you outgrow Redis Streams → NATS JetStream:**
- Redis Streams consumer group semantics map directly to NATS durable pull consumers.
- The main migration cost is deploying NATS alongside Redis.
- Keep Redis for its other uses (cache, rate limiting); replace only the Streams usage.

**If you outgrow NATS → Redis Streams (downsizing):**
- Rare — Redis Streams are typically chosen to avoid adding NATS, not to replace it.
- Valid when a repo already runs Redis-heavy and wants to eliminate the NATS service.

## Seam Type Interaction

From `context/doctrine/multi-backend-coordination.md` — the broker seam type applies to all three options. The choice of broker does not change the seam contract pattern:

| Broker | Best for (seam context) |
|---|---|
| NATS JetStream | Lightweight intra-cluster fan-out; Go↔Elixir, Go↔Go |
| Kafka | Cross-team domain event pipelines; Clojure↔Go, Scala↔Python |
| Redis Streams | Job queues; Elixir↔Go, Python↔Python on existing Redis |

## Related

- context/stacks/nats-jetstream.md
- context/stacks/kafka.md
- context/stacks/redis.md (Redis Streams section)
- context/stacks/coordination-seam-patterns.md
- context/doctrine/multi-backend-coordination.md
