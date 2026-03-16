# Kafka + Trino

Use this combo pack when Kafka topics need to be queryable as SQL tables via Trino. The Kafka connector maps topic messages to queryable rows at query time, enabling ad-hoc stream analytics, cross-source joins, and SQL-level topic inspection without building a consumer pipeline.

Load `context/stacks/kafka.md` for Kafka configuration and producer/consumer patterns. Load `context/stacks/trino.md` for Trino catalog setup and query guidance.

## When to Use This Combo

- Joining Kafka topic data with Postgres or MongoDB tables in a single Trino query (e.g., enrich Kafka payment events with user records from Postgres).
- Ad-hoc analytics over Kafka topics without building a dedicated consumer pipeline.
- Debugging and inspecting topic contents at SQL level.
- BI tools that speak SQL but need access to streaming data without a dedicated consumer.

## Architecture: How the Kafka Connector Works

The Kafka connector maps each Kafka topic to a Trino table. Topic messages are decoded at query time — there is no consumer group and no indexing. Each row is one Kafka message. The connector exposes built-in columns alongside columns defined in a topic table definition file:

| Built-in column      | Type      | Description                                  |
|---|---|---|
| `_partition_id`      | BIGINT    | Kafka partition number                        |
| `_partition_offset`  | BIGINT    | Message offset within the partition           |
| `_message_key`       | VARCHAR   | Raw message key                               |
| `_timestamp`         | TIMESTAMP | Message timestamp set by the broker           |

Trino reads all partitions in parallel — queries scan the full topic unless bounded by offset or timestamp predicates. Use `LIMIT` aggressively in development.

## Kafka Catalog Config

`etc/catalog/kafka.properties`:

```
connector.name=kafka
kafka.nodes=kafka:9092
kafka.table-names=payments.orders.created,analytics.users.churned
kafka.hide-internal-columns=false
kafka.default-schema=default
```

The `kafka.table-names` property lists every topic exposed as a Trino table. Add new topics here when they need to be queryable.

## Topic Table Definition Files

Each topic needs a JSON definition file that maps message fields to Trino column types. Place these in the directory referenced by `kafka.table-description-dir` in the Trino server config.

`etc/kafka/payments.orders.created.json`:

```json
{
  "tableName": "payments.orders.created",
  "schemaName": "default",
  "topicName": "payments.orders.created",
  "message": {
    "dataFormat": "json",
    "fields": [
      {"name": "payload_version", "mapping": "payload_version", "type": "BIGINT"},
      {"name": "correlation_id",  "mapping": "correlation_id",  "type": "VARCHAR"},
      {"name": "published_at",    "mapping": "published_at",    "type": "VARCHAR"},
      {"name": "tenant_id",       "mapping": "tenant_id",       "type": "VARCHAR"},
      {"name": "entity_id",       "mapping": "entity_id",       "type": "VARCHAR"},
      {"name": "risk_score",      "mapping": "data/risk_score", "type": "DOUBLE"},
      {"name": "risk_tier",       "mapping": "data/risk_tier",  "type": "VARCHAR"}
    ]
  }
}
```

The `mapping` field uses `/` for nested JSON path navigation. Top-level fields map directly by name; nested fields use a slash-separated path (e.g., `data/risk_score` maps to `{"data": {"risk_score": 0.12}}`).

## Example Queries

Simple topic scan:

```sql
SELECT correlation_id, tenant_id, risk_score, _timestamp
FROM kafka.default."payments.orders.created"
WHERE risk_tier = 'high'
ORDER BY _timestamp DESC
LIMIT 100;
```

Cross-source join (Kafka topic + Postgres table):

```sql
SELECT k.entity_id, k.risk_score, k.risk_tier,
       p.user_email, p.account_age_days
FROM kafka.default."payments.orders.created" k
JOIN postgresql.app.users p ON k.entity_id = p.order_id
WHERE k.published_at >= '2026-03-01'
  AND k.risk_tier = 'high'
ORDER BY k.risk_score DESC;
```

Partition offset inspection:

```sql
SELECT _partition_id,
       MIN(_partition_offset) AS min_offset,
       MAX(_partition_offset) AS max_offset,
       COUNT(*)               AS message_count
FROM kafka.default."payments.orders.created"
GROUP BY _partition_id;
```

## Local Dev Composition

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

  trino:
    image: trinodb/trino:446
    ports:
      - "8085:8080"
    volumes:
      - ./etc/catalog:/etc/trino/catalog
      - ./etc/kafka:/etc/trino/kafka   # topic table definition files
    depends_on:
      kafka:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/info"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s
```

The `etc/kafka/` volume mount must point to the directory where topic table definition `.json` files live. Set `kafka.table-description-dir=/etc/trino/kafka` in the Trino server config if not set by default.

## Limitations and Anti-Patterns

- **Full topic scan on every query.** The Kafka connector reads all messages and filters locally — there is no index, no pushdown to Kafka. Use `LIMIT` in development. Bound production queries with `WHERE _timestamp > TIMESTAMP '...'` or `_partition_offset` ranges.
- **Not for high-frequency operational queries.** Trino+Kafka is for ad-hoc analysis and cross-source joins, not for hot-path dashboards with sub-second SLA requirements.
- **Message ordering is not guaranteed across partitions.** Use `ORDER BY _partition_id, _partition_offset` when ordered output is required.
- **Avro-encoded topics require Schema Registry.** The JSON decoder will not decode Avro binary messages. If topics use Avro encoding, configure the Avro decoder and provide the Confluent Schema Registry URL in the Trino Kafka catalog config.
- **Read-only.** The Kafka connector is read-only. Any write path goes directly to Kafka producers.

## Related

- `context/stacks/kafka.md`
- `context/stacks/trino.md`
- `context/stacks/duckdb-trino-polars.md`
