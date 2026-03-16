# Seam: Kotlin + Rust via gRPC (Protocol Buffers)

## Purpose

This example demonstrates the gRPC seam between a Kotlin service (caller) and a Rust compute server. The `.proto` file is the centerpiece — both sides generate stubs from it, and the proto file is the source of truth for the seam contract. Kotlin calls Rust synchronously with a typed RPC; Rust computes the result and returns it with the server-side duration.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**gRPC (synchronous, Protocol Buffers)** — Kotlin calls Rust; Rust serves.

## Why Proto Is the Canonical Contract

Both Kotlin and Rust generate their client/server stubs from `service.proto`. The proto file:
- Enforces field types across the language boundary at compile time
- Makes schema evolution explicit — adding fields is backward-compatible; removing or renumbering fields is a breaking change
- Provides a language-agnostic reference that any future language (Go, Python, etc.) can generate stubs from

**Do not hand-write the stubs.** Regenerate them from `service.proto` whenever the contract changes.

## Stub Generation Commands

### Rust (tonic + prost)

```bash
# build.rs handles this automatically via tonic_build.
# Manual generation (if needed):
cargo install protoc-gen-prost protoc-gen-tonic
protoc \
  --prost_out=src/gen \
  --tonic_out=src/gen \
  service.proto
```

In practice, add `build.rs` to the Rust service:
```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("service.proto")?;
    Ok(())
}
```

### Kotlin (protobuf-kotlin + grpc-kotlin)

```bash
# Via Gradle protobuf plugin (recommended — add to build.gradle.kts):
# plugins { id("com.google.protobuf") version "0.9.4" }
# protobuf { generateProtoTasks { all().forEach { task -> task.plugins { id("grpc") {}; id("grpckt") {} } } } }

# Manual generation:
protoc \
  --kotlin_out=src/main/kotlin \
  --grpc-kotlin_out=src/main/kotlin \
  --java_out=src/main/java \
  --plugin=protoc-gen-grpckt=$(which protoc-gen-grpckt) \
  service.proto
```

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/kotlin-rust-grpc
docker compose up --build
```

Note: the first build will take several minutes — Rust compiles from source and Gradle downloads dependencies.

Expected sequence:
1. `rust-service` builds and starts; gRPC server listens on `:50051`; HTTP healthz on `:8082`.
2. `kotlin-service` starts after Rust passes its healthcheck.
3. Kotlin makes a `Compute` RPC call with method `mean` and values `[1.0, 2.0, 3.0, 4.0, 5.0]`.

## What to Observe

- Kotlin log: `Rust response: result=3.0 method=mean duration_ns=<N>`
- Rust stderr: `compute method=mean values=5 result=3.0000 duration_ns=<N>`
- Health endpoints:
  - `curl http://localhost:8082/healthz` → `{"status":"ok"}` (Rust HTTP sidecar)
  - `curl http://localhost:8080/healthz` → `{"status":"ok"}` (Kotlin Ktor; probes Rust gRPC health)

## Build Notes

**Rust build:** `cargo build --release` compiles the Rust server. The `build.rs` file triggers `tonic_build::compile_protos("service.proto")` during compilation. Ensure `protoc` (protobuf compiler) is installed in the build container (`apt-get install protobuf-compiler`).

**Kotlin/Gradle build:** the Gradle `shadowJar` task bundles all dependencies into a fat JAR. The Gradle protobuf plugin generates Kotlin and Java stubs from `service.proto` during the `generateProto` task that runs before `compileKotlin`. Place `service.proto` in `src/main/proto/`.

## Downstream Health Probe

Kotlin's `/healthz` calls the Rust `Check` RPC. If Rust is unreachable or returns `NOT_SERVING`, Kotlin returns `503`. This is the same downstream health probe pattern as the REST example — a service is not healthy if its compute dependency is not healthy.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-kotlin-rust.md`
- `context/stacks/rust-axum-modern.md`
- `context/stacks/coordination-seam-patterns.md`
