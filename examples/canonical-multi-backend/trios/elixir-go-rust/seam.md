# Seam: Elixir + Go + Rust (NATS JetStream + gRPC)

## Purpose

This example demonstrates both seams in the Elixir + Go + Rust trio: Elixir publishes work tasks to NATS JetStream (seam 1, Elixir → Go), Go workers receive each task, call Rust synchronously via gRPC to compute the result (seam 2, Go → Rust), then publish a completion event back through NATS so Elixir can close the coordination loop.

This is a **seam-focused example** — it shows only the coordination layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Architecture

```
[Elixir Coordinator]  ── NATS JetStream ──►  [Go Workers]
       :4000           work.tasks.dispatch          :8080
                                                      │
                                             gRPC (kernel.v1)
                                                      │
                                                      ▼
                                               [Rust Kernel]
                                                  :50051 / :8082
```

Elixir never calls Rust directly. Rust never knows about Elixir. The only cross-language path is:

```
Elixir → NATS → Go → Rust → Go → NATS → Elixir
```

## Why This Trio

**Elixir owns coordination** — not Go. Elixir's OTP supervision trees are the right abstraction for distributed coordination: per-instrument state, retry orchestration, completion tracking across nodes, and fault-isolated process trees. Elixir decides *when* work is dispatched.

**Go owns execution** — not Elixir. Go's lightweight goroutine pool and direct gRPC client make it the natural executor: it subscribes to the NATS work queue, calls Rust, and reports back. Using Elixir processes for this role would sacrifice Go's throughput advantage without gaining OTP's supervision benefits.

**Rust owns compute** — not Go. The compute step (normalize, mean, etc.) must be sub-millisecond and GC-free. Rust's deterministic latency and zero overhead make it the right kernel. Go's GC would introduce unpredictable pause times on the hot path.

This topology is the **inverse** of `trios/go-elixir-python/`, where Go is the publisher and Elixir is the subscriber. Here, Elixir is the publisher (coordinator) and Go is the subscriber (executor). This reflects the rule from `context/doctrine/multi-backend-coordination.md`: the language that owns coordination state should be the publisher.

## Seam Types

**Seam 1 (Elixir → Go): Broker seam via NATS JetStream**
**Seam 2 (Go → Rust): gRPC seam via Protocol Buffers (kernel.v1)**

## Seam 1: Elixir → Go via NATS JetStream

### Why Elixir publishes (not Go)

Elixir owns the coordination layer — it decides when work is dispatched, handles retries (via OTP supervision), and monitors completion. Go is a stateless executor: it receives a task and processes it. Putting the dispatch decision in Go would require Go to maintain coordination state, which is Elixir's role.

### JetStream stream: WORK_TASKS

- Stream: `WORK_TASKS`, subjects: `work.tasks.>`
- Dispatch subject: `work.tasks.dispatch` (Elixir → Go)
- Completion subject: `work.tasks.completed` (Go → Elixir, loop-back)

The `work.tasks.>` pattern captures both subjects in one stream. JetStream stores messages durably until Go's consumer acks them — if Go workers restart, messages are redelivered.

### Task event (Elixir → Go)

```json
{
  "payload_version": 1,
  "task_id": "task-demo-001",
  "correlation_id": "coord-001",
  "published_at": "2026-03-16T10:00:00Z",
  "task_type": "compute.normalize",
  "data": {"values": [1.0, 3.0, 5.0, 2.0, 4.0], "operation": "normalize"}
}
```

### Multiple Go workers — NATS distributes

Multiple Go worker instances can subscribe to the same durable consumer `go-workers`. NATS JetStream distributes messages across active subscribers as a work queue — each task is delivered to exactly one worker. This is horizontal worker scaling without a separate queue manager.

### Completion event (Go → Elixir, loop-back)

```json
{
  "payload_version": 1,
  "task_id": "task-demo-001",
  "correlation_id": "coord-001",
  "published_at": "2026-03-16T10:00:00.001Z",
  "result_summary": "normalize 5 values",
  "duration_ns": 87000
}
```

## Seam 2: Go → Rust via gRPC

### Proto file: kernel.v1 (shared with scala-rust-grpc)

This Rust server implements the **same `kernel.v1` proto** as `duos/scala-rust-grpc/`. This is intentional: the Rust compute kernel is reusable across different callers. A Scala Akka Streams pipeline and a Go worker pool can both call the same Rust server without modification.

```protobuf
service KernelService {
  rpc Transform(TransformRequest) returns (TransformResponse);
}

message TransformRequest {
  string operation = 1;
  repeated double values = 2;
  int32 window_size = 3;
}

message TransformResponse {
  repeated double result = 1;
  string method = 2;
  int64 duration_ns = 3;
}
```

### Why gRPC (not REST)

- Per-task compute call on repeated float arrays — binary encoding efficiency
- Typed contract: `TransformRequest`/`TransformResponse` enforced at stub generation time
- Rust tonic server: single-threaded async runtime is not appropriate; use the default multi-threaded `#[tokio::main]`
- Call latency matters: the gRPC round-trip for a normalize operation is sub-millisecond

### Supported operations

| operation | behavior |
|---|---|
| `normalize` | Min-max scale to [0.0, 1.0] |
| `mean` | Returns mean as single-element array |
| (other) | Returns values unchanged |

Input `[1.0, 3.0, 5.0, 2.0, 4.0]` → normalize → `[0.0, 0.5, 1.0, 0.25, 0.75]`

## Dependency Ordering

```
nats          (no dependencies; starts first)
rust-kernel   (no dependencies; starts first alongside NATS)
go-workers    depends on: nats (service_healthy), rust-kernel (service_healthy)
elixir-coordinator  depends on: nats (service_healthy) ONLY
```

Elixir does **not** depend on Go. NATS JetStream stores messages durably — if Go workers are not yet ready when Elixir publishes, the WORK_TASKS stream retains the task until Go subscribes. This is the broker seam's durability guarantee: the producer and consumer do not need to start in strict order.

## How to Run Locally

```bash
cd examples/canonical-multi-backend/trios/elixir-go-rust
docker compose up --build
```

Note: Rust compiles from source. First build takes several minutes.

Expected sequence:
1. NATS starts with JetStream enabled (`:4222`, `:8222`).
2. `rust-kernel` compiles and starts gRPC on `:50051`, health sidecar on `:8082`.
3. `go-workers` starts after NATS and Rust pass healthchecks; subscribes to `work.tasks.dispatch`.
4. `elixir-coordinator` starts after NATS passes its healthcheck; publishes the demo task.
5. Go receives the task, calls Rust, publishes completion; Elixir receives and logs the completion.

## What to Observe

```
# Elixir logs:
elixir-coordinator: subscribed to work.tasks.completed
task published to NATS: task_id=task-demo-001 subject=work.tasks.dispatch

# Go logs:
task received from NATS: task_id=task-demo-001 operation=normalize values=[1 3 5 2 4]
Rust result: task_id=task-demo-001 operation=normalize result=[0 0.5 1 0.25 0.75] duration_ns=<N>
completion published: task_id=task-demo-001 subject=work.tasks.completed result_summary="normalize 5 values"

# Rust stderr:
Transform called: operation=normalize input_len=5 result_len=5 duration_ns=<N>

# Elixir logs (loop-back):
completion received from Go: task_id=task-demo-001 result_summary=normalize 5 values duration_ns=<N>
```

The closed coordination loop:
```
Elixir publishes task → NATS durably stores → Go receives → Go calls Rust →
Rust computes → Go publishes completion → NATS delivers → Elixir receives confirmation
```

## Health Endpoints

```bash
curl http://localhost:8082/healthz   # Rust HTTP sidecar → {"status":"ok"}
curl http://localhost:8080/healthz   # Go — probes both NATS and Rust gRPC
wget -q -O- http://localhost:4000/healthz  # Elixir — checks coordinator process
```

Stop Rust and check Go health:

```bash
docker compose stop rust-kernel
curl http://localhost:8080/healthz
# → 503 {"status":"degraded","nats_ok":true,"rust_ok":false}
```

## Stub Generation

### Go (from repo root after copying service.proto)

```bash
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest

protoc --go_out=. --go-grpc_out=. \
       --go_opt=paths=source_relative \
       --go-grpc_opt=paths=source_relative \
       service.proto
# Generates: gen/kernel/v1/service.pb.go and service_grpc.pb.go
```

### Rust (via build.rs — runs automatically during `cargo build`)

```bash
# build.rs handles this:
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("service.proto")?;
    Ok(())
}
```

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/trio-elixir-go-rust.md`
- `context/stacks/duo-go-elixir.md`
- `context/stacks/duo-elixir-rust.md`
- `context/stacks/nats-jetstream.md`
- `context/stacks/grpc.md`
- `context/stacks/coordination-seam-patterns.md`
- `examples/canonical-multi-backend/duos/scala-rust-grpc/` — Rust kernel with Scala caller (same kernel.v1 proto)
- `examples/canonical-multi-backend/duos/go-elixir-nats/` — Go publishes, Elixir subscribes (inverted topology)
