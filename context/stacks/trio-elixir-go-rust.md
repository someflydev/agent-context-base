# Trio: Elixir + Go + Rust

The fault-tolerant high-performance trio: Elixir owns distributed coordination and process supervision, Go runs the high-throughput external-facing API layer and fast worker pools, and Rust handles sub-millisecond compute kernels that cannot tolerate runtime overhead. The two design tensions this trio resolves are reliability vs. throughput (Elixir's supervisor trees and Go's goroutine pool serve their respective concerns without compromise) and throughput vs. latency (Go handles volume efficiently while Rust handles the hot path at sub-millisecond latencies). The target archetype is a low-latency distributed system: high-frequency trading infrastructure, game server backends, telemetry processing at scale, and systems where both fault tolerance and deterministic compute latency are non-negotiable.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Distributed coordination, OTP supervision trees, per-node state, retry orchestration | Elixir |
| Multi-node cluster membership and fault isolation | Elixir |
| External-facing HTTP APIs, fast worker pool, ingestion layer, service mesh integration | Go |
| Sub-millisecond compute: financial matching, search indexing, cryptographic operations | Rust |
| NATS event publishing (coordination events) and consumer supervision | Elixir |
| NATS event consumption, work dispatch to Rust | Go |
| Seam A↔B contract (Elixir → Go via NATS JetStream) | Elixir + Go |
| Seam B↔C contract (Go → Rust via gRPC) | Go + Rust |

## Seam Map

```
[Elixir Coordinator]  ──── NATS JetStream ────►  [Go Services]
       :4000                                           :8080
                                                          │
                                                        gRPC
                                                          │
                                                          ▼
                                                    [Rust Kernel]
                                                       :50051
```

Elixir publishes coordination events to NATS (e.g., "process this work unit", "invalidate this cache segment", "route this job to a worker"). Go workers consume these events, call Rust synchronously via gRPC for the latency-critical compute step, and report results back to Elixir via a completion event or REST callback.

Elixir never calls Rust directly. Rust never knows about Elixir. The only cross-language path is: Elixir → NATS → Go → Rust.

## Communication Contracts

### Seam A↔B: Elixir → Go via NATS JetStream

Stream: `COORDINATION`, subjects: `coord.>`

Event published by Elixir to `coord.work.dispatch`:

```json
{
  "payload_version": 1,
  "correlation_id": "coord-001",
  "published_at": "2026-03-16T10:00:00Z",
  "work_unit_id": "wu-9182",
  "operation": "compute_signal",
  "parameters": {
    "instrument": "AAPL",
    "window_size": 50
  }
}
```

Go publishes completion results to `coord.work.completed`:

```json
{
  "payload_version": 1,
  "correlation_id": "coord-001",
  "work_unit_id": "wu-9182",
  "result": 0.0042,
  "duration_ns": 87000,
  "completed_at": "2026-03-16T10:00:00.001Z"
}
```

### Seam B↔C: Go → Rust via gRPC

Proto file: `kernel.proto` (package `kernel.v1`)

```protobuf
syntax = "proto3";
package kernel.v1;

service KernelService {
  rpc Compute(ComputeRequest) returns (ComputeResponse);
}

message ComputeRequest {
  string operation  = 1;
  repeated double values = 2;
  map<string, string> params = 3;
}

message ComputeResponse {
  double result      = 1;
  int64  duration_ns = 2;
}
```

Go calls Rust:

```bash
# RUST_GRPC_URL = rust-service:50051
resp, err := kernelClient.Compute(ctx, &pb.ComputeRequest{
    Operation: "compute_signal",
    Values:    []float64{1.1, 2.2, 3.3},
    Params:    map[string]string{"window": "50"},
})
# resp.Result: 0.0042
# resp.DurationNs: 87000
```

## Local Dev Composition

```yaml
services:
  nats:
    image: nats:2.10-alpine
    command: "-js"
    ports:
      - "4222:4222"
      - "8222:8222"
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s

  rust-service:
    build: ./services/rust
    ports:
      - "50051:50051"
      - "8090:8090"
    environment:
      GRPC_PORT: "50051"
      HTTP_PORT: "8090"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  go-service:
    build: ./services/go
    ports:
      - "8080:8080"
    environment:
      NATS_URL: "nats://nats:4222"
      RUST_GRPC_URL: "rust-service:50051"
    depends_on:
      nats:
        condition: service_healthy
      rust-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  elixir-service:
    build: ./services/elixir
    ports:
      - "4000:4000"
    environment:
      NATS_URL: "nats://nats:4222"
      GO_SERVICE_URL: "http://go-service:8080"
    depends_on:
      nats:
        condition: service_healthy
      go-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s
```

## Health Contract

Dependency order (bottom to top):

1. **NATS** — no dependencies; starts first. Signals readiness at `http://nats:8222/healthz`.
2. **Rust** — no dependencies; starts first alongside NATS. Signals readiness at `GET http://localhost:8090/healthz → 200 {"status":"ok"}`. Runs an HTTP sidecar alongside the gRPC server specifically for healthcheck purposes.
3. **Go** — depends on NATS (direct) and Rust (direct). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after establishing NATS subscription and confirming Rust gRPC is reachable. Returns `503` if either is unavailable.
4. **Elixir** — depends on NATS (direct) and Go (direct, which transitively implies Rust is healthy). Signals readiness at `GET /healthz → 200 {"status":"ok"}` after establishing NATS connection and confirming Go's health endpoint.

This ordering ensures Elixir will not publish coordination events until the full downstream chain (Go → Rust) is ready to process them.

## When to Use This Trio

- **High-frequency financial systems**: Elixir manages order books and distributed per-instrument state across nodes, Go handles external market data ingestion and order routing, Rust runs the matching engine or signal computation at sub-millisecond latency.
- **Game server infrastructure**: Elixir coordinates game sessions, player state machines, and matchmaking across nodes, Go handles the high-throughput game event API, Rust runs physics simulation or collision detection kernels.
- **Telemetry processing at scale**: Elixir supervises per-device event streams and routes telemetry work, Go handles the external ingestion HTTP/gRPC layer, Rust computes aggregations and anomaly signals at high frequency.
- **Low-latency data transformation pipelines**: Elixir coordinates transformation topology and fault recovery, Go handles parallelism and worker pool scheduling, Rust applies CPU-bound transformations to data frames.

## When NOT to Use This Trio

- **Go can handle the compute directly**: if the compute kernel does not require sub-millisecond latency or memory-safe systems-level code, Go's performance is often sufficient and the Rust gRPC seam adds ceremony without measurable gain.
- **No distributed coordination required**: if the system is a single-node service without multi-node state or supervised retry trees, drop Elixir and use `duo-go-rust` instead.
- **Elixir is being used only as a queue wrapper**: if Elixir's role reduces to "publish a NATS message", a Go worker pool can replace it. Elixir earns its place only when OTP supervision trees and multi-node distributed state provide genuine value.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/elixir-phoenix.md`
- `context/stacks/go-echo.md`
- `context/stacks/rust-axum-modern.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/duo-go-elixir.md`
- `context/stacks/duo-elixir-rust.md`
- `context/stacks/duo-kotlin-rust.md`
