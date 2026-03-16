# Kafka

Use this pack when the repo adds a distributed, partitioned event streaming layer for high-throughput pipelines. Kafka is the right broker when message volumes are high (millions/day), cross-team schema contracts are required, or consumers need independent offset tracking and long-term log retention.

## When Kafka Is the Right Choice

- Message volumes that benefit from horizontal partition scaling (millions/day threshold).
- Cross-team consumer compatibility requires a schema registry (Avro, Protobuf, JSON Schema).
- Strict ordering guarantees needed within a partition key (e.g., all events for the same `tenant_id` land in the same partition).
- Long-term message retention (days/weeks) needed for replay or audit.
- The consumer ecosystem already uses Kafka client libraries.
- Multiple independent consumer groups reading the same topic at different offsets.

## When Kafka Is NOT the Right Choice

- Lightweight event bus with simple per-subject routing → use NATS JetStream.
- In-memory streams with consumer groups on existing Redis infrastructure → use Redis Streams.
- Small volume (< 100k messages/day) without schema registry need.
- Local dev environment where KRaft/ZooKeeper setup adds friction without benefit.
- Real-time request/response patterns → use gRPC or REST.
- Ordering not needed and fan-out is simple → NATS is operationally simpler.

## Typical Repo Surface

- `app/messaging/producer.py` — Kafka producer setup, message construction, publish logic
- `app/messaging/consumer.py` — consumer group setup, poll loop, manual offset commit, DLQ routing
- `etc/kafka/topic-init.sh` — topic creation script run at startup
- `tests/integration/test_kafka_pipeline.py` — produce one message, consume and assert; DLQ path
- `docker-compose.test.yml` — bitnami/kafka with KRaft (no ZooKeeper)

## Core Concepts

### Topics

A topic is a named, ordered, partitioned log. Messages are appended and retained until the configured retention period expires. Unlike queues, topics do not remove messages after consumption — multiple consumer groups can read the same topic independently.

### Partitions

Each topic is divided into one or more partitions. Within a partition, messages are strictly ordered. The partition key determines which partition a message lands in: messages with the same key always go to the same partition.

Partition count is set at topic creation. Increasing partition count is possible but triggers a rebalance and can disrupt ordering guarantees for existing consumers.

### Consumer Groups

A consumer group is a set of consumers that share a group ID. Kafka assigns each partition to exactly one consumer in the group at a time. Multiple groups can subscribe to the same topic and receive all messages independently.

When a consumer in the group fails, Kafka reassigns its partitions to other members — this is a rebalance.

### Offsets

Each message in a partition has a monotonically increasing offset. Consumers track their position using offsets. A consumer commits its offset to signal that messages up to that offset have been processed. With `enable.auto.commit=false` (manual commit), the consumer controls exactly when to advance its offset.

## Topic Naming Convention

```
{domain}.{entity}.{event_type}
```

- Dot-separated, lowercase.
- Examples: `payments.orders.created`, `analytics.users.churned`, `inventory.items.updated`
- Partition key: `tenant_id` or `entity_id` — the field that should co-locate related events in the same partition.
- Avoid verb-named topics like `process-order`. Topics are event logs, not task queues.

## Schema Strategy

### JSON (no registry)

Fast to start, human-readable, no tooling overhead. Good for internal single-team services. Document the schema in `docs/seam-contract/` alongside the code.

### Avro + Schema Registry (Confluent or Apicurio)

Best for cross-team or cross-service compatibility. The registry enforces backward/forward compatibility guarantees on each schema change. Use `confluent_kafka` with `SchemaRegistryClient` (Python) or jackdaw with schema registry support (Clojure).

Avro schema file (`.avsc`):
```json
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.example.payments",
  "fields": [
    {"name": "payload_version", "type": "int"},
    {"name": "correlation_id", "type": "string"},
    {"name": "tenant_id",      "type": "string"},
    {"name": "entity_id",      "type": "string"},
    {"name": "published_at",   "type": "string"}
  ]
}
```

Register the schema before publishing:
```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

registry = SchemaRegistryClient({"url": os.getenv("SCHEMA_REGISTRY_URL")})
```

### JSON Schema Registry

An intermediate option — human-readable schema with registry enforcement, without Avro binary encoding. Use when cross-team schema agreement is needed but Avro binary format is not required.

## Producer Patterns

Python producer (`pip install confluent-kafka`):

```python
import json, os, time, logging
from confluent_kafka import Producer

log = logging.getLogger(__name__)

conf = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    "acks": "all",              # strongest durability: all in-sync replicas must ack
    "enable.idempotence": True, # exactly-once producer semantics at the broker level
    "retries": 5,
    "retry.backoff.ms": 200,
}
producer = Producer(conf)

def publish_event(topic: str, key: str, event: dict) -> None:
    payload = json.dumps({
        "payload_version": 1,
        "correlation_id": event.get("correlation_id", ""),
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **event
    }).encode()
    producer.produce(topic, key=key.encode(), value=payload, callback=delivery_report)
    producer.poll(0)  # trigger callbacks without blocking

def delivery_report(err, msg):
    if err:
        log.error("delivery failed: %s", err)
    else:
        log.info("delivered to %s [%d] @ offset %d",
                 msg.topic(), msg.partition(), msg.offset())
```

Clojure producer (jackdaw, `deps.edn: fundingcircle/jackdaw {:mvn/version "0.9.12"}`):

```clojure
(require '[jackdaw.client :as jc]
         '[cheshire.core :as json])

(def producer-config
  {"bootstrap.servers"  (System/getenv "KAFKA_BOOTSTRAP_SERVERS")
   "acks"               "all"
   "enable.idempotence" "true"
   "key.serializer"     "org.apache.kafka.common.serialization.StringSerializer"
   "value.serializer"   "org.apache.kafka.common.serialization.StringSerializer"})

(defn publish-event [producer topic key event]
  @(jc/produce! producer
                {:topic-name topic}
                (str key)
                (json/encode event)))
```

## Consumer Patterns

Python consumer (manual offset commit, at-least-once semantics):

```python
import json, os, logging
from confluent_kafka import Consumer, KafkaError, KafkaException

log = logging.getLogger(__name__)

conf = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    "group.id": "my-consumer-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,   # manual commit for at-least-once
}
consumer = Consumer(conf)
consumer.subscribe(["payments.orders.created"])

while True:
    msg = consumer.poll(timeout=1.0)
    if msg is None:
        continue
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            continue
        raise KafkaException(msg.error())
    event = json.loads(msg.value())
    try:
        process_event(event)
        consumer.commit(asynchronous=False)   # commit only after successful processing
    except Exception as e:
        send_to_dlq(event, str(e))
        consumer.commit(asynchronous=False)   # commit DLQ'd messages too; don't stall the partition
```

Go consumer (franz-go, `go.mod: github.com/twmb/franz-go v1.x`):

```go
import (
    "context"
    "github.com/twmb/franz-go/pkg/kgo"
)

func startConsumer(ctx context.Context, brokers []string, topic, groupID string) error {
    cl, err := kgo.NewClient(
        kgo.SeedBrokers(brokers...),
        kgo.ConsumerGroup(groupID),
        kgo.ConsumeTopics(topic),
        kgo.DisableAutoCommit(),
    )
    if err != nil {
        return err
    }
    defer cl.Close()

    for {
        fetches := cl.PollFetches(ctx)
        if err := fetches.Err(); err != nil {
            return err
        }
        fetches.EachRecord(func(r *kgo.Record) {
            if err := processRecord(r); err != nil {
                logDLQ(r, err)
            }
            cl.CommitRecords(ctx, r)
        })
    }
}
```

## Dead Letter Topics

- Pattern: `{original_topic}.dlq`
- Example: `payments.orders.created.dlq`
- Send to DLQ when: deserialization fails, schema version unsupported, business rule rejects the event, max retries exceeded.
- DLQ payload must include: original message bytes, error message, retry count, `failed_at` timestamp.
- Consumer groups should have a dedicated DLQ monitor service that alerts on backlog growth.

## Local Dev Composition

Primary recommendation: bitnami/kafka with KRaft (ZooKeeper-free, single container):

```yaml
services:
  kafka:
    image: bitnami/kafka:3.7
    ports:
      - "9092:9092"
    environment:
      KAFKA_CFG_NODE_ID: "1"
      KAFKA_CFG_PROCESS_ROLES: "broker,controller"
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_CFG_LISTENERS: "PLAINTEXT://:9092,CONTROLLER://:9093"
      KAFKA_CFG_ADVERTISED_LISTENERS: "PLAINTEXT://kafka:9092"
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: "PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT"
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: "true"
    healthcheck:
      test: ["CMD", "kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--list"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s
```

Full platform option (confluentinc/cp-kafka + ZooKeeper): use only when a Confluent Schema Registry is also required. Add `confluentinc/cp-zookeeper` and `confluentinc/cp-schema-registry` to the compose file. See `context/stacks/kafka-trino.md` for the Trino combo setup.

## Testing Expectations

- Run integration tests against a real Kafka broker (Docker-backed bitnami/kafka with KRaft).
- Prove one produce + consume round-trip with a real message.
- Prove DLQ delivery for a malformed message.
- Test idempotent re-delivery: produce the same message twice; verify the consumer handles the duplicate correctly.
- Do NOT mock the Kafka client in integration tests — broker behavior (offset commits, consumer group rebalance, DLQ routing) is what is being tested.
- Isolate test topics per test run using a unique `group.id` suffix or unique topic names with a run timestamp.

## Common Assistant Mistakes

- Using `enable.auto.commit=True` — this commits before processing is confirmed, causing message loss on crash. Always use manual commit.
- Creating topics inside the consumer at message time — create topics at startup with explicit partition count and replication factor.
- Naming topics as verbs (`process-payment`) instead of event log nouns (`payments.transactions.created`).
- Reusing consumer group IDs across environments — dev and test must have separate group IDs.
- Ignoring the DLQ — assuming all messages will process successfully without a dead-letter path.
- Using confluentinc/cp-kafka in docker-compose without a Schema Registry when Avro is planned.

## Related

- `context/stacks/nats-jetstream.md` — lighter alternative for smaller volumes
- `context/stacks/kafka-trino.md` — Kafka as a Trino-queryable data source
- `context/doctrine/broker-selection.md` — three-way NATS vs Kafka vs Redis Streams decision
- `context/stacks/coordination-seam-patterns.md` — Kafka broker seam implementation
- `context/stacks/duo-clojure-go.md` — primary Kafka duo
- `context/stacks/trio-clojure-python-go.md` — Kafka in a trio pipeline
- `examples/canonical-multi-backend/duos/clojure-go-kafka/` — canonical seam example
