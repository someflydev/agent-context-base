# gRPC (Protocol Buffers)

Authoritative reference for gRPC as a cross-language seam technology. Consult this doc whenever a gRPC seam is chosen in `context/workflows/design-multi-backend-seams.md`. For how gRPC fits into multi-backend coordination (when to choose it over REST or a broker), see `context/stacks/coordination-seam-patterns.md`.

---

## When gRPC Is the Right Choice

- **Schema enforcement across language boundaries is required.** The `.proto` file is the canonical contract; breaking changes are caught at stub generation time rather than at runtime.
- **Synchronous results are required** — the caller waits for a typed response.
- **Performance matters for the call itself.** Proto binary encoding is more compact and faster to serialize/deserialize than JSON, especially for repeated numeric fields (e.g., feature vectors).
- **Streaming is needed.** Server-streaming, client-streaming, and bidirectional streaming RPCs are all expressible in proto and handled by gRPC natively — no WebSocket or long-poll workaround needed.
- **The service pair includes Rust (tonic), Go (google.golang.org/grpc), Kotlin (grpc-kotlin), or Scala (ScalaPB)** — all have excellent, production-grade gRPC support.

---

## When gRPC Is NOT the Right Choice

- **Simple request/response where JSON readability is preferred** → use REST with FastAPI or Echo. No proto ceremony, human-readable schema, auto-generated OpenAPI spec.
- **The caller is a browser.** gRPC-Web is possible but adds a proxy layer and complexity; use REST or GraphQL instead.
- **Both services are the same language and the call is in-process** → function call. No network seam needed.
- **The schema will change frequently in early development.** Proto field numbers must be stable once published; removing or renumbering fields is a breaking change. REST with JSON is more forgiving at the cost of runtime errors instead of build-time errors.
- **The team is unfamiliar with protoc and does not want to manage stub generation steps.** The compilation ceremony (protoc, plugins, per-language output dirs) is real overhead. Only accept it when the schema enforcement benefit justifies it.

---

## Proto File Organization

- All `.proto` files live in `docs/seam-contract/` or a shared `proto/` directory at the repo root — not inside either service's source tree. Both services read from the same location.
- **Package naming:** `{domain}.{version}` — e.g., `inference.v1`, `compute.v1`, `processing.v1`.
- **`go_package` option:** required for Go stub generation; use your module path.
- **One service per `.proto` file.** Keep the file small and focused on a single bounded concern.
- Add API-level comments to every service, RPC, message, and field.
- **Never reuse field numbers.** Once a field is added, its number is permanent. Use `reserved` to document removed fields:
  ```protobuf
  reserved 4;
  reserved "old_field";
  ```
- Always start field numbers at 1. Never use 19000–19999 (reserved by the protobuf runtime).

### Well-structured example proto

```protobuf
// docs/seam-contract/inference.proto
syntax = "proto3";
package inference.v1;

// go_package required for Go codegen
option go_package = "github.com/example/myapp/gen/inference/v1;inferencev1";

// InferenceService handles ML model prediction requests.
service InferenceService {
  // Predict runs a single inference over the provided features.
  rpc Predict(PredictRequest) returns (PredictResponse);

  // PredictStream accepts a stream of requests and returns a stream of responses.
  // Use for batched inference where the client sends multiple requests.
  rpc PredictStream(stream PredictRequest) returns (stream PredictResponse);
}

// PredictRequest carries the feature vector for a single inference.
message PredictRequest {
  // model_id identifies which model to use. Required.
  string model_id = 1;

  // features is the numeric feature vector. Required; must be non-empty.
  repeated float features = 2;

  // correlation_id is propagated for distributed tracing. Optional.
  string correlation_id = 3;
}

// PredictResponse carries the inference result.
message PredictResponse {
  // label is the predicted class name.
  string label = 1;

  // confidence is the probability of the predicted class (0.0–1.0).
  float confidence = 2;

  // duration_ns is the server-side inference duration in nanoseconds.
  int64 duration_ns = 3;
}
```

---

## RPC Method Types

**Unary:** `rpc Predict(Request) returns (Response)`
- One request, one response. Use for synchronous query/response patterns. Most seam patterns in this repo use unary.

**Server-streaming:** `rpc Scan(ScanRequest) returns (stream ScanResult)`
- One request, stream of responses. Use for paginated results, progress updates, or incremental delivery.

**Client-streaming:** `rpc Upload(stream Chunk) returns (UploadResult)`
- Stream of requests, one response. Use for file upload or batched writes.

**Bidirectional streaming:** `rpc Chat(stream Msg) returns (stream Msg)`
- Full-duplex stream. Use for real-time protocols (voice, game state, live collaboration).

**Default:** use unary. Only add streaming when the use case requires it — streaming adds meaningful complexity to error handling, deadline propagation, and backpressure on both sides.

---

## Stub Generation (per language)

Run these commands from the repo root (where the `.proto` file is located in `docs/seam-contract/`).

### Go

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

protoc --go_out=gen --go_opt=paths=source_relative \
       --go-grpc_out=gen --go-grpc_opt=paths=source_relative \
       docs/seam-contract/inference.proto
```

Requires `go_package` option in the proto file. The generated files land in `gen/`.

### Rust (tonic-build via build.rs)

No standalone `protoc` invocation needed. tonic-build runs during `cargo build`.

```toml
# Cargo.toml
[build-dependencies]
tonic-build = "0.12"
```

```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("../../docs/seam-contract/inference.proto")?;
    Ok(())
}
```

Requires `protoc` installed in the build environment: `apt-get install protobuf-compiler`.

### Python

```bash
pip install grpcio-tools

python -m grpc_tools.protoc \
    -I docs/seam-contract \
    --python_out=gen \
    --pyi_out=gen \
    --grpc_python_out=gen \
    docs/seam-contract/inference.proto
```

Generates `inference_pb2.py`, `inference_pb2.pyi`, and `inference_pb2_grpc.py`.
Use `grpcio` (C extension), not `grpclib` (pure Python), for production workloads.

### Kotlin (Gradle protobuf plugin)

```kotlin
// build.gradle.kts
plugins { id("com.google.protobuf") version "0.9.4" }

dependencies {
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")
    implementation("com.google.protobuf:protobuf-kotlin:3.25.0")
}

protobuf {
    protoc { artifact = "com.google.protobuf:protoc:3.25.0" }
    plugins {
        id("grpc") { artifact = "io.grpc:protoc-gen-grpc-java:1.62.2" }
        id("grpckt") { artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.1:jdk8@jar" }
    }
    generateProtoTasks {
        all().forEach { it.plugins { id("grpc"); id("grpckt") } }
    }
}
```

Place `.proto` files in `src/main/proto/`. Gradle generates Kotlin and Java stubs automatically during the `generateProto` task.

### Scala (ScalaPB via sbt)

```scala
// build.sbt
libraryDependencies ++= Seq(
  "io.grpc"               % "grpc-netty"           % "1.62.2",
  "com.thesamet.scalapb" %% "scalapb-runtime-grpc" % scalapb.compiler.Version.scalapbVersion,
)

Compile / PB.targets := Seq(
  scalapb.gen(grpc = true) -> (Compile / sourceManaged).value / "scalapb"
)
```

Stubs are generated into `target/scala-*/src_managed/` during `sbt compile`.

### Elixir

> **Note:** gRPC is NOT idiomatic for Elixir as a seam. Prefer NATS (via Gnat) or REST for Elixir services. If gRPC is required:

```elixir
# mix.exs dep: {:grpc, "~> 0.8"}
# Generate stubs: mix grpc.gen --proto=docs/seam-contract/inference.proto
```

---

## Error Handling

gRPC status codes to know and use correctly:

| Code | Number | Meaning |
|---|---|---|
| `OK` | 0 | Success |
| `DEADLINE_EXCEEDED` | 4 | Call deadline elapsed before completion |
| `NOT_FOUND` | 5 | Entity not found |
| `ALREADY_EXISTS` | 6 | Conflicts with existing state |
| `PERMISSION_DENIED` | 7 | Caller authenticated but not authorized |
| `RESOURCE_EXHAUSTED` | 8 | Rate limit or quota exceeded |
| `INVALID_ARGUMENT` | 3 | Caller sent bad input |
| `INTERNAL` | 13 | Unexpected server error — do not expose internal details |
| `UNAVAILABLE` | 14 | Server temporarily unavailable; safe to retry with backoff |
| `UNAUTHENTICATED` | 16 | Caller not authenticated |

Use the most specific code available. Do not return `INTERNAL` for input validation errors.

**Rust (tonic):**
```rust
return Err(Status::invalid_argument("features must not be empty"));
return Err(Status::not_found(format!("model {} not found", req.model_id)));
```

**Go:**
```go
return nil, status.Errorf(codes.InvalidArgument, "features must not be empty")
return nil, status.Errorf(codes.NotFound, "model %s not found", req.ModelId)
```

**Python:**
```python
context.abort(grpc.StatusCode.INVALID_ARGUMENT, "features must not be empty")
context.abort(grpc.StatusCode.NOT_FOUND, f"model {request.model_id} not found")
```

---

## Deadlines and Timeouts

**Always set a deadline on the caller side.** A missing deadline means a hung downstream can block the caller indefinitely.

**Go:**
```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
resp, err := client.Predict(ctx, req)
```

**Python:**
```python
response = stub.Predict(request, timeout=5.0)
```

**Kotlin:**
```kotlin
stub.withDeadlineAfter(5, TimeUnit.SECONDS).predict(request)
```

**Rust (tonic):**
```rust
use std::time::Duration;
use tonic::Request;

let mut req = Request::new(predict_request);
req.set_timeout(Duration::from_secs(5));
let response = client.predict(req).await?;
```

---

## Interceptors

Interceptors (called middleware in some frameworks) run on every RPC call — useful for logging, authentication, tracing, and retry logic.

**Go (server-side interceptor):**
```go
func loggingInterceptor(
    ctx context.Context,
    req interface{},
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    log.Printf("rpc=%s duration=%s err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

// Register at startup:
grpc.NewServer(grpc.UnaryInterceptor(loggingInterceptor))
```

**Rust (tonic):** Use `tower` middleware via `ServiceBuilder`. tonic servers accept `tower::Service` layers:
```rust
use tower::ServiceBuilder;
// wrap the service before passing to Server::builder().add_service()
```

**Python:** Use `grpc.ServerInterceptor` subclass. Intercept `intercept_service` to wrap handlers.

Keep interceptors to logging, tracing, and auth token extraction. Do not put business logic in interceptors.

---

## Health Checking Standard

Use `grpc.health.v1.Health/Check` — the standard gRPC health checking protocol. Both sides should implement it.

Proto import: `grpc/health/v1/health.proto` (available in the grpc-health-probe repository).

**Simpler alternative (preferred in this repo):** expose an HTTP `/healthz` alongside the gRPC server. This avoids requiring `grpc_health_probe` in the container and works with `curl` in docker-compose health checks.

Rust (tonic) pattern — run Axum or a minimal hyper HTTP server on a sidecar port alongside the gRPC server via `tokio::spawn`:

```rust
// Spawn HTTP healthz on HEALTH_PORT; gRPC on GRPC_PORT
tokio::spawn(async move { run_health_server(health_port).await });
Server::builder()
    .add_service(InferenceServiceServer::new(InferenceImpl::default()))
    .serve(grpc_addr)
    .await?;
```

docker-compose healthcheck without grpc_health_probe:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8082/healthz"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 20s
```

---

## Reflection and grpc-gateway

**gRPC server reflection** (`grpc.reflection.v1alpha.ServerReflection`): allows tools like `grpcurl` and `grpc-ui` to introspect the server without the `.proto` file.

- **Rust (tonic):** add the `tonic-reflection` crate; register the file descriptor set at startup.
- **Go:** add `google.golang.org/grpc/reflection`; call `reflection.Register(server)` at startup.
- Enable in dev; consider disabling in production to avoid exposing the schema.

**grpc-gateway:** generates an HTTP/JSON reverse proxy from the proto file, allowing REST clients to reach a gRPC service. Add `google.api.http` annotations to proto methods, then run `protoc-gen-grpc-gateway`. Useful when a browser or REST-only client must reach a gRPC service without a separate BFF layer.

---

## Local Dev Composition

Rust gRPC server with HTTP healthz sidecar + a calling service:

```yaml
services:
  inference-kernel:
    build:
      context: ./services/kernel
      dockerfile: Dockerfile
    ports:
      - "50051:50051"   # gRPC
      - "8082:8082"     # HTTP /healthz sidecar
    environment:
      GRPC_PORT: "50051"
      HEALTH_PORT: "8082"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s  # Rust compile is slow on first build

  gateway:
    build:
      context: ./services/gateway
    ports:
      - "8080:8080"
    environment:
      GRPC_KERNEL_ADDR: inference-kernel:50051
    depends_on:
      inference-kernel:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
```

---

## Testing Expectations

- **Test stub generation:** run protoc and verify generated files compile in each target language.
- **Prove one unary RPC round-trip with a real server** — no mocks. The stub generation and wire behavior is what you are testing.
- **Prove error handling:** call with invalid input; verify the correct gRPC status code is returned (not `INTERNAL` for a validation error).
- **Prove deadline handling:** make a request to a slow server; verify `DEADLINE_EXCEEDED` is returned.
- **Prove health check:** call `/healthz` or `Health/Check`; verify `200`/`SERVING`.
- **Do NOT mock the gRPC server in integration tests.** Mocking removes the proto contract from the test surface, which is the primary value of the gRPC seam.
- Keep test protos separate from production protos if testing error injection scenarios.

---

## Common Assistant Mistakes

- **Not setting `go_package` in the proto file.** Go codegen fails without it. Add it even if you do not plan Go clients immediately.
- **Reusing or skipping field numbers.** Once a field number is assigned, it is permanent. Removing or renumbering fields silently breaks binary-format compatibility for any client not regenerating stubs from the new proto.
- **Not setting a deadline on the caller side.** A hung downstream will block the caller indefinitely. Always set a timeout.
- **Using `INTERNAL` status code for all errors.** Use the most specific code available. `INVALID_ARGUMENT` for bad input, `NOT_FOUND` for missing entities, `UNAVAILABLE` for transient failures.
- **Forgetting to run protoc after changing the proto.** Stubs become stale; the mismatch is silent until the mismatched field is accessed.
- **Not exposing an HTTP health endpoint alongside gRPC.** docker-compose health checks are far simpler with `curl` than with `grpc_health_probe` (which requires installing the tool in the container).
- **Running Rust tonic server on a single async runtime thread.** Use `#[tokio::main]` (which defaults to multi-thread) and do not override the runtime flavor to `current_thread` unless the workload is provably single-threaded.

---

## Related

- `context/stacks/coordination-seam-patterns.md` — gRPC seam in the context of multi-backend coordination (summary + quick-start patterns)
- `context/stacks/rust-axum-modern.md` — Rust side: tonic gRPC server + Axum/hyper HTTP sidecar
- `context/stacks/go-echo.md` — Go side: grpc client from an Echo service
- `context/stacks/scala-tapir-http4s-zio.md` — Scala side: ScalaPB client
- `context/doctrine/multi-backend-coordination.md` — when to use gRPC as the seam type
- `examples/canonical-multi-backend/duos/rust-python-grpc/` — Rust tonic server + Python grpcio client
- `examples/canonical-multi-backend/duos/kotlin-rust-grpc/` — Kotlin grpc-kotlin client + Rust tonic server
- `examples/canonical-multi-backend/duos/scala-rust-grpc/` — Scala ScalaPB + Rust (added in PROMPT_59)
