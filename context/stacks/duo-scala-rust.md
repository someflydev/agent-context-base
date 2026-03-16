# Duo: Scala + Rust

Scala and Rust combine to form a financial data or observability pipeline where Scala orchestrates distributed streams using Akka Streams or Apache Spark and Rust handles the compute kernels that exceed JVM latency budgets. Scala's actor model and streaming DSLs are unmatched for complex distributed topology; Rust provides SIMD-accelerated computation, predictable GC-free latency, and memory safety for the stages that would cause GC pauses in the JVM. The gRPC seam lets Scala delegate hot-path stages to Rust without abandoning the streaming topology.

## Division of Labor

| Responsibility | Owner |
|---|---|
| Stream topology orchestration (Akka Streams / Spark) | Scala |
| Distributed actor coordination | Scala |
| Schema evolution and serialization logic | Scala |
| Batch analytics and aggregate reporting | Scala |
| SIMD-accelerated data transforms (hot path) | Rust |
| Low-latency compute kernels (aggregation, encoding) | Rust |
| Memory-safe native library operations | Rust |
| gRPC server and request handling | Rust |
| Seam contract | Both |

## Primary Seam

gRPC seam via Protocol Buffers: Scala Akka Streams delegates compute-intensive stages to the Rust kernel server via gRPC when the stage exceeds JVM GC latency budget; Rust returns typed results synchronously.

## Communication Contract

```protobuf
// docs/seam-contract/kernel.proto
syntax = "proto3";
package kernel.v1;

service KernelService {
  rpc Transform(TransformRequest) returns (TransformResponse);
}

message TransformRequest {
  string operation    = 1;   // e.g. "rolling_mean", "normalize", "fft"
  repeated double values = 2;
  int32  window_size  = 3;
}

message TransformResponse {
  repeated double result  = 1;
  string  method          = 2;
  int64   duration_ns     = 3;
}
```

Scala caller (scalapb + grpc):
```scala
import kernel.v1.{KernelServiceGrpc, TransformRequest}
import io.grpc.ManagedChannelBuilder

val channel = ManagedChannelBuilder
  .forTarget(sys.env.getOrElse("RUST_KERNEL_ADDR", "rust-kernel:50051"))
  .usePlaintext()
  .build()
val stub = KernelServiceGrpc.stub(channel)

val response = stub.transform(TransformRequest(
  operation = "rolling_mean",
  values = Seq(1.0, 2.0, 3.0, 4.0, 5.0),
  windowSize = 3
))
// response.result, response.durationNs
```

## Local Dev Composition

```yaml
services:
  rust-kernel:
    build:
      context: ./services/kernel
      dockerfile: Dockerfile
    ports:
      - "50051:50051"
      - "8082:8082"   # HTTP /healthz sidecar
    environment:
      GRPC_PORT: "50051"
      HEALTH_PORT: "8082"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  scala-streams:
    build:
      context: ./services/streams
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      RUST_KERNEL_ADDR: rust-kernel:50051
      PORT: "8080"
    depends_on:
      rust-kernel:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 40s
```

## Health Contract

- **rust-kernel**: `GET /healthz` → `200 {"status":"ok"}` on HTTP sidecar port (Axum router alongside tonic); also supports `grpc.health.v1.Health/Check`
- **scala-streams**: `GET /healthz` → `200 {"status":"ok"}` (Akka HTTP route or http4s endpoint); probes Rust kernel gRPC reachability; returns `503` if kernel is unreachable

## When to Use This Duo

- Financial market data pipelines where Scala Akka Streams handles topology orchestration and Rust performs SIMD-accelerated rolling aggregations too hot for JVM GC.
- Observability systems (metrics, traces, logs) where Scala manages the ingestion topology and Rust handles binary encoding and compression at the write path.
- Scientific computing pipelines where Scala orchestrates distributed work and Rust handles the FFT, matrix operations, or signal processing kernels.
- Teams already on Scala/Akka who need to optimize specific stages for latency — Rust via gRPC is a surgical insertion rather than a rewrite.
- Systems where JVM GC pause spikes are measured and confirmed to cause latency SLA violations — use profiler data to justify the Rust boundary.

## When NOT to Use This Duo

- The streaming workload is I/O-bound — Akka Streams with backpressure handles I/O throughput well; Rust does not help here.
- GC pause analysis has not been done — do not add Rust speculatively; profile first and only split when the data justifies the seam.
- The team is JVM-only — Rust expertise is required to own the kernel service; without it, the seam becomes a maintenance liability.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/rust-axum-modern.md
- context/stacks/coordination-seam-patterns.md
