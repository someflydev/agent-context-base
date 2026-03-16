# Seam: Scala + Rust via gRPC (Akka Streams)

## Purpose

This example demonstrates the gRPC seam between a Scala Akka Streams pipeline (orchestrator/caller) and a Rust tonic gRPC server (compute kernel). The Scala side runs a streaming pipeline that delegates per-element compute to Rust via `mapAsync` — the central integration pattern from `context/stacks/duo-scala-rust.md`.

This is a **seam-focused example** — it shows only the integration layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Type

**gRPC (synchronous, Protocol Buffers)** — Scala Akka Streams calls Rust; Rust serves.

## Why gRPC (not REST)

- **Typed contract for numeric arrays.** `repeated double values` in the proto enforces the field type across the language boundary at compile time. A REST API would require JSON encoding/decoding on both sides with no compile-time schema enforcement.
- **Binary encoding efficiency.** Proto binary encoding is more compact and faster to serialize than JSON, especially for `repeated double` fields — common in financial data, signal processing, and ML feature vectors.
- **Low-latency per-element RPC.** The Scala pipeline calls Rust for each `InputRecord`. gRPC's persistent HTTP/2 connection reuse eliminates per-request TCP handshake overhead, making per-element calls feasible.

## Why Akka Streams (not plain Scala)

- **Backpressure.** Akka Streams backpressure ensures Scala does not overwhelm the Rust service. When all `mapAsync` parallelism slots are occupied, the `Source` is signaled to stop producing elements until a slot opens.
- **Controlled concurrency via `mapAsync(parallelism)`.**
  - `parallelism = 1`: serial — each element waits for the previous RPC to complete.
  - `parallelism = N`: up to N RPCs are in-flight simultaneously; backpressure applies when all N are busy.
  - This is preferable to spawning unlimited futures or goroutines, which can saturate the Rust server.
- **Composability.** Additional pipeline stages (validation, enrichment, persistence) can be added as `Flow` operators without changing the gRPC integration point.

## The Proto File as the Canonical Contract

`service.proto` is the source of truth for this seam. Both Scala and Rust generate their stubs from it:

- **Rust:** `tonic_build::compile_protos("service.proto")` in `build.rs` generates `kernel.v1` types during `cargo build`.
- **Scala:** `sbt-akka-grpc` generates `KernelServiceClient` and message types during `sbt compile`.

**Do not hand-write the stubs.** Regenerate them from `service.proto` whenever the contract changes.

The proto package is `kernel.v1` with field names that match `duo-scala-rust.md`'s Communication Contract exactly:
- `TransformRequest.operation`, `.values` (repeated double), `.window_size`
- `TransformResponse.result` (repeated double), `.method`, `.duration_ns`

This proto uses a **different package** (`kernel.v1`) than `rust-python-grpc/service.proto` (`inference.v1`). Do not conflate them.

## Stub Generation

### Rust (tonic-build via build.rs)

No standalone `protoc` invocation needed. `tonic-build` runs during `cargo build`:

```toml
# Cargo.toml
[build-dependencies]
tonic-build = "0.12"
```

```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("service.proto")?;
    Ok(())
}
```

Requires `protoc` installed in the build environment (`apt-get install protobuf-compiler`).

### Scala (sbt-akka-grpc)

Add the plugin to `project/plugins.sbt`:

```scala
addSbtPlugin("com.lightbend.akka.grpc" % "sbt-akka-grpc" % "2.4.0")
```

Enable in `build.sbt`:

```scala
enablePlugins(AkkaGrpcPlugin)

libraryDependencies += "com.lightbend.akka.grpc" %% "akka-grpc-runtime" % "2.4.0"
```

Place `service.proto` in `src/main/protobuf/`. The plugin generates `KernelServiceClient` and message types into `target/scala-*/src_managed/` during `sbt compile`.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/duos/scala-rust-grpc
docker compose up --build
```

**Note:** the first build will take several minutes — Rust compiles from source (`cargo build --release`) and sbt downloads dependencies and compiles Scala + generates gRPC stubs.

Expected sequence:
1. `rust-kernel` builds (Rust compile), starts; gRPC server listens on `:50051`; HTTP healthz on `:8082`.
2. `scala-pipeline` starts after `rust-kernel` passes its healthcheck.
3. Scala creates 5 synthetic `InputRecord` items and runs the Akka Streams pipeline.
4. For each record, `mapAsync(parallelism = 2)` calls `KernelService.Transform` on the Rust server.
5. Scala logs the result for each record.

## What to Observe

- **Scala logs:**
  ```
  id=rec-001 operation=normalize result=[-1.4142, -0.7071, 0.0000, 0.7071, 1.4142] duration_ns=<N>
  id=rec-002 operation=normalize result=[-1.4142, -0.7071, 0.0000, 0.7071, 1.4142] duration_ns=<N>
  ...
  Pipeline completed successfully
  ```
- **Rust stderr:**
  ```
  KernelService gRPC listening on 0.0.0.0:50051
  HTTP healthz listening on 0.0.0.0:8082
  transform operation=normalize values=5 result_len=5 duration_ns=<N>
  ```
- **Health endpoints:**
  - `curl http://localhost:8082/healthz` → `{"status":"ok"}` (Rust HTTP sidecar)
  - `curl http://localhost:8080/healthz` → `{"status":"ok"}` (Scala Akka HTTP)

## Build Notes

**Rust build:** `cargo build --release` compiles the Rust kernel. `build.rs` triggers `tonic_build::compile_protos("service.proto")` during compilation. Requires `protoc` (protobuf compiler) in the build container.

**Scala/sbt build:** `sbt assembly` bundles all dependencies into a fat JAR. The `sbt-akka-grpc` plugin generates Scala stubs from `service.proto` during the `compile` task. Place `service.proto` in `src/main/protobuf/`.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/duo-scala-rust.md`
- `context/stacks/akka-streams.md`
- `context/stacks/grpc.md`
- `context/stacks/rust-axum-modern.md`
- `context/stacks/coordination-seam-patterns.md`
