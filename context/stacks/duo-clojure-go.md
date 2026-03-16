# Duo: Clojure + Go

Clojure and Go combine to form an event-driven business platform where Clojure owns the complex domain logic — business rule engines, Kafka Streams topologies, and rich data transformation — and Go owns the high-throughput execution tier: external APIs, fast consumer workers, and operational tooling. Clojure's Lisp-family expressiveness and immutable data model are a natural fit for business rules; Go's goroutine model and single-binary deployment make it the right runtime for the consumer workers that execute at scale.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Business rule engines and domain logic | Clojure |
| Kafka Streams topology and event enrichment | Clojure |
| Complex data transformation (map-centric) | Clojure |
| High-throughput external API and HTTP handlers | Go |
| Fast Kafka consumer workers and batch processors | Go |
| Operational tooling and CLI utilities | Go |
| Seam contract | Both |

## Primary Seam

Broker seam via Kafka: Clojure produces enriched domain events to Kafka topics; Go consumes them at high throughput using franz-go or confluent-kafka-go.

## Communication Contract

Kafka topic: `domain.orders.enriched` (partition key: `tenant_id`)

Event schema (Avro-compatible JSON for documentation; use schema registry in production):
```json
{
  "payload_version": 1,
  "correlation_id": "req-abc-123",
  "published_at": "2026-03-16T10:30:00Z",
  "tenant_id": "finco",
  "event_type": "order.risk_scored",
  "entity_id": "ord-9987",
  "data": {
    "risk_score": 0.12,
    "risk_tier": "low",
    "rule_version": "2026-Q1",
    "triggered_rules": ["velocity_check", "geo_mismatch"]
  }
}
```

Field notes:
- `payload_version`: Go consumers reject unknown versions explicitly
- `rule_version`: tracks which Clojure rule set produced the event
- `triggered_rules`: bounded array — at most ~20 entries; never embed large nested objects

## Local Dev Composition

```yaml
services:
  kafka:
    image: bitnami/kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_CFG_NODE_ID: "1"
      KAFKA_CFG_PROCESS_ROLES: broker,controller
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
      ALLOW_PLAINTEXT_LISTENER: "yes"
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions.sh", "--bootstrap-server", "localhost:9092"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s

  clojure-rules:
    build:
      context: ./services/rules
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    environment:
      KAFKA_BOOTSTRAP: kafka:9092
      INPUT_TOPIC: domain.orders.raw
      OUTPUT_TOPIC: domain.orders.enriched
    depends_on:
      kafka:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  go-worker:
    build:
      context: ./services/worker
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      KAFKA_BOOTSTRAP: kafka:9092
      CONSUME_TOPIC: domain.orders.enriched
      CONSUMER_GROUP: go-worker-grp
    depends_on:
      kafka:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s
```

Note: bitnami/kafka 3.x uses KRaft mode — no Zookeeper required.

## Health Contract

- **clojure-rules**: `GET /healthz` → `200 {"status":"ok"}` (Ring/Compojure or http-kit handler); degrades if Kafka consumer group is lagging beyond threshold
- **go-worker**: `GET /healthz` → `200 {"status":"ok"}`; includes consumer group lag check; returns `503` if lag exceeds configured threshold

## When to Use This Duo

- Fintech or insurtech platforms where business rules are complex, frequently changing, and best expressed as Clojure data-driven rule engines (e.g., Clara Rules, custom map transforms).
- Event sourcing systems where Clojure enriches raw events into rich domain events and Go executes the downstream side effects at scale.
- Teams with a Clojure data team and a Go platform team — the Kafka seam maps cleanly to the organizational boundary.
- High-volume consumer pipelines (millions of events/day) where Kafka's horizontal partitioning is needed and Clojure's Kafka Streams DSL is already in use.
- Systems that need schema evolution guarantees — the Kafka schema registry with Avro or Protobuf protects both producers and consumers across deploy cycles.

## When NOT to Use This Duo

- Low event volume — NATS JetStream is far simpler to operate than a Kafka cluster; consider a different language pair.
- The business logic is simple enough for Go — do not add Clojure just because rules exist; only when the rules are complex enough to benefit from Clojure's data-driven expressiveness.
- The team has no JVM experience — Clojure on the JVM has a startup and ops overhead; if Go alone can handle the domain logic, keep it single-language.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/coordination-seam-patterns.md
