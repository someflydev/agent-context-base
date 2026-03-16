# Canonical Multi-Backend Examples

## Purpose

These examples show the seam layer between coordinating backend services. Each example is seam-focused, not a full application: it demonstrates only the connection setup, message/request send and receive, and health endpoint for each side of the boundary. Internal application logic for each language follows from the corresponding stack doc in `context/stacks/`. The goal is to show exactly what crosses the seam and how both sides establish and maintain the contract.

## Catalog

| Directory | Languages | Seam Type | Use Case |
|---|---|---|---|
| `duos/go-elixir-nats/` | Go + Elixir | Broker (NATS JetStream) | Event fan-out to real-time clients |
| `duos/go-python-rest/` | Go + Python | REST (HTTP/JSON) | ML scoring gateway |
| `duos/kotlin-rust-grpc/` | Kotlin + Rust | gRPC (Protocol Buffers) | Compute kernel |
| `trios/go-elixir-python/` | Go + Elixir + Python | Broker + REST | Gateway + coordination + ML |
| `trios/go-rust-python/` | Go + Rust + Python | gRPC + REST | Gateway + kernel + ML |

## Seam Types

**Broker seam (NATS JetStream or Kafka):** one service publishes events to a broker subject or topic; one or more services subscribe and consume independently. The seam is asynchronous and decoupled — the publisher does not wait for the consumer. Use this when fan-out is required, when strict coupling between the two sides is undesirable, or when both sides have independent scaling profiles. See `context/stacks/coordination-seam-patterns.md` for the full broker seam pattern.

**REST seam (HTTP/JSON):** one service calls another via HTTP, receives a synchronous response, and decodes a JSON body. The seam is synchronous and self-documenting — FastAPI generates an OpenAPI spec automatically, and the schema is readable without tooling. Use this when request/response semantics are sufficient and the call frequency does not demand proto compilation. See `context/stacks/coordination-seam-patterns.md` for the REST seam pattern and downstream health probe pattern.

**gRPC seam (Protocol Buffers):** one service calls another via a typed RPC, generated from a `.proto` file that both sides share. The seam is synchronous, strongly typed, and language-agnostic — stubs are generated for each language from the same source. Use this when schema enforcement across language boundaries is important, when performance matters for the call itself, or when streaming RPCs are needed. See `context/stacks/coordination-seam-patterns.md` for the gRPC seam pattern and stub generation commands.

## How to Run an Example

Each example is self-contained. Start with any of the duo examples:

```bash
# Broker seam — Go publishes, Elixir subscribes
cd examples/canonical-multi-backend/duos/go-elixir-nats
docker compose up --build
# observe logs from go-service (publish) and elixir-service (consume + decode)

# REST seam — Go gateway calls Python scoring
cd examples/canonical-multi-backend/duos/go-python-rest
docker compose up --build
# curl http://localhost:8080/run-inference to trigger a round-trip

# gRPC seam — Kotlin caller, Rust compute server
cd examples/canonical-multi-backend/duos/kotlin-rust-grpc
docker compose up --build
# observe Kotlin logs showing the Rust response: result, method, duration_ns
```

Trio examples (three-service compositions):

```bash
# Broker + REST — Go publishes to NATS, Elixir coordinates, Elixir calls Python
cd examples/canonical-multi-backend/trios/go-elixir-python
docker compose up --build
# curl -X POST http://localhost:8080/submit-job -d '{"job_id":"j1","features":[1,2,3]}'

# gRPC + REST — Go calls Rust (preprocess) then Python (score) in sequence
cd examples/canonical-multi-backend/trios/go-rust-python
docker compose up --build   # first build takes several minutes (Rust compile)
# curl -X POST http://localhost:8080/process -d '{"document":"hello world","doc_id":"d1"}'
```

Read the `seam.md` companion doc in each directory before reading the code. It explains the directional choice, the event/request schema, and what to observe when running locally.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/` — `duo-*.md` and `trio-*.md` docs
- `context/archetypes/multi-backend-service.md`
- `context/stacks/coordination-seam-patterns.md`
