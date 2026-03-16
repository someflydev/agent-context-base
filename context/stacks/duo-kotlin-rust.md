# Duo: Kotlin + Rust

Kotlin and Rust combine to form a mobile platform backend where Kotlin owns the full JVM service tier — user accounts, billing, auth, Spring/Ktor application services — and Rust owns the performance-critical compute layer: media encoding, search indexing, cryptographic operations, or any workload where JVM GC pauses are unacceptable. Kotlin provides the enterprise integration depth of the JVM ecosystem; Rust provides the deterministic performance profile that heavy compute demands. The gRPC seam lets Kotlin call Rust synchronously with a typed, versioned contract.

## Division of Labor

| Responsibility | Owner |
|---|---|
| User and account management | Kotlin |
| Billing, subscription, and entitlement logic | Kotlin |
| Auth and token verification (JWT, OAuth) | Kotlin |
| Spring/Ktor service APIs and database persistence | Kotlin |
| Media encoding, search indexing, crypto operations | Rust |
| CPU-bound compute with deterministic latency | Rust |
| gRPC server implementation | Rust |
| Seam contract | Both |

## Primary Seam

gRPC seam via Protocol Buffers: Kotlin services call the Rust compute server using `grpc-kotlin` coroutine stubs; Rust serves requests using `tonic`.

## Communication Contract

```protobuf
// docs/seam-contract/compute.proto
syntax = "proto3";
package compute.v1;

service ComputeService {
  rpc Process(ProcessRequest) returns (ProcessResponse);
}

message ProcessRequest {
  string job_id    = 1;
  string operation = 2;   // e.g. "encode_h264", "index_search", "derive_key"
  bytes  payload   = 3;
}

message ProcessResponse {
  string job_id      = 1;
  bytes  result      = 2;
  int64  duration_ns = 3;
}
```

Kotlin caller (grpc-kotlin coroutines):
```kotlin
val channel = ManagedChannelBuilder
    .forTarget(System.getenv("RUST_COMPUTE_ADDR") ?: "rust-compute:50051")
    .usePlaintext()
    .build()
val stub = ComputeServiceGrpcKt.ComputeServiceCoroutineStub(channel)

val response = stub.process(processRequest {
    jobId = "job-abc"
    operation = "encode_h264"
    payload = ByteString.copyFrom(rawVideoBytes)
})
// response.result, response.durationNs
```

## Local Dev Composition

```yaml
services:
  rust-compute:
    build:
      context: ./services/compute
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

  kotlin-api:
    build:
      context: ./services/api
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      RUST_COMPUTE_ADDR: rust-compute:50051
      PORT: "8080"
      DATABASE_URL: jdbc:postgresql://postgres:5432/app
    depends_on:
      rust-compute:
        condition: service_healthy
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "app"]
      interval: 5s
      timeout: 3s
      retries: 5
```

## Health Contract

- **rust-compute**: `GET /healthz` → `200 {"status":"ok"}` on HTTP sidecar port (Axum router alongside tonic, or a minimal hyper server); also supports `grpc.health.v1.Health/Check` for `grpc_health_probe`
- **kotlin-api**: `GET /actuator/health` → `200 {"status":"UP"}` (Spring Boot Actuator); probes Rust compute reachability; returns `DOWN` if compute gRPC is unreachable

## When to Use This Duo

- Mobile platform backends where Kotlin/Spring handles user accounts, billing, and push notifications, and Rust handles media processing (thumbnails, video transcoding, audio encoding).
- Search platforms where Kotlin manages the user-facing search API and indexing job scheduling, and Rust runs the compute-intensive indexing and scoring kernels.
- Security products requiring cryptographic operations (key derivation, certificate signing, encryption) that must be deterministic and memory-safe.
- JVM shops adding a Rust compute service to relieve GC-pause-induced latency spikes on their hottest paths.
- Teams exploring Rust incrementally — the gRPC boundary is a clean insertion point that doesn't require rewriting existing Kotlin services.

## When NOT to Use This Duo

- The compute workload is I/O-bound rather than CPU-bound — Kotlin's coroutines and virtual threads handle I/O concurrency well without Rust.
- JVM GC pauses are not causing latency problems — profile first; only split if the data confirms Rust is necessary.
- The team has no Rust expertise — a Kotlin-only service with tuned JVM settings may be sufficient; add Rust when there is a clear owner.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/rust-axum-modern.md
- context/stacks/coordination-seam-patterns.md
- examples/canonical-multi-backend/duos/kotlin-rust-grpc/
