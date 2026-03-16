# Trio: Clojure + Python + Go

The business intelligence pipeline trio: Clojure processes and enriches domain events using a functional rules engine and Kafka Streams topology, Python scores the enriched events using ML models, and Go serves the scored results through a low-latency read API. The two design tensions this trio resolves are business rule expressiveness vs. ML scoring (Clojure's data transformation power handles complex rule logic cleanly while Python handles the probabilistic scoring that rule engines cannot express) and ML computation vs. fast serving (Python's batch-friendly inference is decoupled from the low-latency read path that Go owns). The target archetype is a risk analytics or business intelligence pipeline: insurance underwriting, credit scoring, fraud detection, financial risk stratification, or healthcare risk modeling.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Event processing, Kafka Streams topology, business rule engines | Clojure |
| Domain event enrichment, data transformation, structural normalization | Clojure |
| ML scoring, model inference, risk assessment, classification | Python |
| Batch analytics, feature engineering, model training pipelines | Python |
| Low-latency read API, result serving, operational microservices | Go |
| Health monitoring endpoints, alerting hooks, ops tooling | Go |
| Seam A↔B contract (Clojure → Python via Kafka) | Clojure + Python |
| Seam B↔C contract (Python → Go via REST) | Python + Go |

## Seam Map

```
[Clojure Events]  ──── Kafka ────►  [Python Scorer]  ──── REST ────►  [Go API]
     :8180                               :8001                            :8080
```

Clojure produces enriched domain events to a Kafka topic. Python consumes those events, runs inference, and writes scored results either to a store that Go reads from or directly to Go's ingest endpoint. Go serves the results to clients via a fast REST API.

The direction is unidirectional and forward-flowing: events move from Clojure to Python to Go. Go does not call Clojure; Python does not call Clojure. Downstream services never push back upstream through these seams.

## Communication Contracts

### Seam A↔B: Clojure → Python via Kafka

Topic: `domain.events.enriched`

Event produced by Clojure:

```json
{
  "payload_version": 1,
  "correlation_id": "evt-001",
  "published_at": "2026-03-16T10:00:00Z",
  "entity_id": "applicant-9182",
  "entity_type": "loan_application",
  "enriched_features": {
    "annual_income": 72000,
    "debt_to_income": 0.31,
    "months_employed": 48,
    "num_credit_lines": 7,
    "derogatory_marks": 0
  },
  "applied_rules": ["income_threshold_check", "dti_rule_v2"]
}
```

Python reads this from Kafka (using `confluent-kafka-python` or `faust`), extracts `enriched_features`, and scores the entity.

### Seam B↔C: Python → Go via REST (HTTP/JSON)

After scoring, Python POSTs the result to Go's ingest endpoint:

Request (`POST /ingest/scored-result`):

```bash
curl -X POST http://go-service:8080/ingest/scored-result \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "applicant-9182",
    "entity_type": "loan_application",
    "score": 0.12,
    "risk_tier": "low",
    "model_version": "credit-v4",
    "scored_at": "2026-03-16T10:00:01Z",
    "correlation_id": "evt-001"
  }'
```

Go acknowledges:

```json
{"status": "accepted", "entity_id": "applicant-9182"}
```

Go clients then read scored results via:

```bash
curl http://go-service:8080/api/v1/entities/applicant-9182/score
# {"entity_id": "applicant-9182", "score": 0.12, "risk_tier": "low", "scored_at": "2026-03-16T10:00:01Z"}
```

## Local Dev Composition

```yaml
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    healthcheck:
      test: ["CMD", "bash", "-c", "echo ruok | nc localhost 2181"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      zookeeper:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s

  go-service:
    build: ./services/go
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  python-service:
    build: ./services/python
    ports:
      - "8001:8001"
    environment:
      KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
      GO_INGEST_URL: "http://go-service:8080"
    depends_on:
      kafka:
        condition: service_healthy
      go-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  clojure-service:
    build: ./services/clojure
    ports:
      - "8180:8180"
    environment:
      KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    depends_on:
      kafka:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8180/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s
```

## Health Contract

Dependency order (bottom to top):

1. **Zookeeper + Kafka** — infrastructure, no service dependencies. Kafka signals readiness via `kafka-broker-api-versions`.
2. **Go** — no application-level dependencies (it serves an ingest endpoint that Python will POST to). Signals readiness at `GET /healthz → 200 {"status":"ok"}`.
3. **Python** — depends on Kafka (to consume enriched events) and Go (to POST scored results). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after confirming both Kafka connectivity and Go `/healthz`.
4. **Clojure** — depends on Kafka (to produce events). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after establishing Kafka producer connectivity. Clojure does not depend on Python or Go — it fires events to Kafka without caring whether Python is ready.

Note: Clojure will produce events to Kafka before Python is consuming them. Kafka's durable log ensures no events are lost — Python will catch up when it starts. This is the expected behavior for a broker-decoupled pipeline.

## When to Use This Trio

- **Insurance underwriting**: Clojure applies underwriting rules and enriches applicant data, Python scores applicants against actuarial risk models, Go serves underwriter decision dashboards.
- **Credit scoring pipelines**: Clojure enriches loan application events with bureau data and business rules, Python runs credit risk models, Go serves the scored decisions to loan origination systems.
- **Fraud detection**: Clojure processes transaction events with behavioral rules, Python scores transaction feature vectors against fraud models, Go serves real-time fraud decisions to authorization APIs.
- **Healthcare risk stratification**: Clojure enriches patient events with clinical rule logic, Python applies risk stratification models, Go serves risk tier results to care management platforms.
- All three are necessary because: Clojure's Kafka Streams and functional data transformation is better suited to complex rule engines than Python; Python's ML ecosystem is irreplaceable for probabilistic scoring; Go's low-latency read API outperforms Python for the serving layer under read load.

## When NOT to Use This Trio

- **Rules are simple enough for Python**: if the enrichment logic is a few conditionals rather than a full rule engine, Python can handle both enrichment and scoring. Add Clojure only when the rule complexity benefits from a functional transformation model.
- **Volume doesn't justify Kafka**: if event volume is low (under ~10k/day), NATS JetStream provides the same decoupling with far less operational overhead than Kafka plus Zookeeper. Swap the seam type rather than the architecture.
- **Go can be replaced by Python for serving**: if the API team is Python-native and latency requirements are relaxed, a second FastAPI service can serve the results instead of Go. Add Go only when read latency is a genuine requirement.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/clojure-kit-nextjdbc-hiccup.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/go-echo.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/duo-clojure-go.md`
- `context/stacks/duo-rust-python.md`
