# Coordination Seam Patterns

Reference doc for implementing the four seam types used in multi-backend systems. Consult this after `design-multi-backend-seams.md` has determined the seam type. Each section shows the canonical pattern for the most common language pairings.

---

## Broker Seam (NATS JetStream)

Use when the producer needs to fire-and-forget events that one or more consumers process independently. Do not use for synchronous request/response — add a gRPC or REST seam for that.

Full NATS JetStream guidance: `context/stacks/nats-jetstream.md`

### Publisher side — Go (nats.go)

```go
// go.mod: github.com/nats-io/nats.go v1.x
import (
    "encoding/json"
    "github.com/nats-io/nats.go"
)

type IngestEvent struct {
    PayloadVersion int    `json:"payload_version"`
    CorrelationID  string `json:"correlation_id"`
    PublishedAt    string `json:"published_at"`
    TenantID       string `json:"tenant_id"`
    RecordID       string `json:"record_id"`
}

func publishEvent(nc *nats.Conn, event IngestEvent) error {
    js, err := nc.JetStream()
    if err != nil {
        return err
    }
    payload, err := json.Marshal(event)
    if err != nil {
        return err
    }
    _, err = js.Publish("events.ingested."+event.TenantID, payload)
    return err
}
```

### Subscriber side — Elixir (Gnat)

```elixir
# mix.exs dep: {:gnat, "~> 1.7"}

defmodule MyApp.EventConsumer do
  use GenServer

  def start_link(_opts) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def init(state) do
    {:ok, conn} = Gnat.start_link(%{host: System.get_env("NATS_HOST", "nats"), port: 4222})
    # Create durable pull consumer (assumes stream already exists)
    {:ok, _} = Gnat.ConsumerSupervisor.start_link(%{
      connection_name: conn,
      module: __MODULE__,
      subscription_topics: [%{topic: "events.ingested.>"}]
    })
    {:ok, Map.put(state, :conn, conn)}
  end

  def handle_message(%{topic: _topic, body: body}) do
    event = Jason.decode!(body)
    # validate payload_version before processing
    case event["payload_version"] do
      1 -> process_v1(event)
      v -> {:error, "unknown payload_version #{v}"}
    end
  end

  defp process_v1(event) do
    # business logic here
    :ok
  end
end
```

### docker-compose.yml snippet

```yaml
services:
  nats:
    image: nats:latest
    command: "-js"
    ports:
      - "4222:4222"   # client
      - "8222:8222"   # HTTP monitoring
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3

  gateway:
    build: ./services/gateway
    environment:
      NATS_URL: nats://nats:4222
    depends_on:
      nats:
        condition: service_healthy

  coordinator:
    build: ./services/coordinator
    environment:
      NATS_HOST: nats
    depends_on:
      nats:
        condition: service_healthy
```

### Stream and consumer creation

Create the stream at application startup (idempotent — safe to call on every boot):

```go
// Go — create stream on startup
js.AddStream(&nats.StreamConfig{
    Name:     "EVENTS",
    Subjects: []string{"events.ingested.>"},
    MaxAge:   24 * time.Hour,
})
```

```elixir
# Elixir — create stream on startup (using Gnat.Jetstream)
Gnat.Jetstream.API.Stream.create(:gnat, %{
  name: "EVENTS",
  subjects: ["events.ingested.>"]
})
```

### Kafka variant

Prefer Kafka over NATS when: message volume is very high (millions/day), a schema registry is needed for cross-team compatibility, or ordering guarantees must span multiple partitions. See `context/stacks/nats-jetstream.md` for the threshold discussion.

Kafka publisher in Clojure (using `clj-kafka` or `jackdaw`):
```clojure
;; deps: [fundingcircle/jackdaw "0.9.x"]
(require '[jackdaw.client :as jc])

(defn publish-event [producer topic event]
  @(jc/produce! producer {:topic-name topic}
                          (str (:correlation-id event))
                          (cheshire.core/encode event)))
```

---

## gRPC Seam (Protocol Buffers)

Use when the caller needs a synchronous, typed result and schema enforcement across language boundaries is important.

### Minimal .proto file

```protobuf
// docs/seam-contract/inference.proto
syntax = "proto3";
package inference.v1;
option go_package = "github.com/example/myapp/gen/inference/v1";

service InferenceService {
  rpc Predict(PredictRequest) returns (PredictResponse);
}

message PredictRequest {
  string model_id = 1;
  repeated float features = 2;
}

message PredictResponse {
  string label       = 1;
  float  confidence  = 2;
}
```

Generate stubs:
```bash
# Go client stubs
protoc --go_out=. --go-grpc_out=. docs/seam-contract/inference.proto

# Python server stubs
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. \
    docs/seam-contract/inference.proto
```

### Server side — Rust (tonic)

```toml
# Cargo.toml
[dependencies]
tonic = "0.11"
prost = "0.12"
tokio = { version = "1", features = ["full"] }

[build-dependencies]
tonic-build = "0.11"
```

```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("../../docs/seam-contract/inference.proto")?;
    Ok(())
}
```

```rust
// src/main.rs
use tonic::{transport::Server, Request, Response, Status};

pub mod inference {
    tonic::include_proto!("inference.v1");
}

use inference::inference_service_server::{InferenceService, InferenceServiceServer};
use inference::{PredictRequest, PredictResponse};

#[derive(Default)]
pub struct InferenceImpl;

#[tonic::async_trait]
impl InferenceService for InferenceImpl {
    async fn predict(
        &self,
        request: Request<PredictRequest>,
    ) -> Result<Response<PredictResponse>, Status> {
        let req = request.into_inner();
        // run inference on req.features
        Ok(Response::new(PredictResponse {
            label: "positive".to_string(),
            confidence: 0.92,
        }))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "0.0.0.0:50051".parse()?;
    Server::builder()
        .add_service(InferenceServiceServer::new(InferenceImpl::default()))
        .serve(addr)
        .await?;
    Ok(())
}
```

### Client side — Go (google.golang.org/grpc)

```go
// go.mod: google.golang.org/grpc v1.x
import (
    "context"
    "google.golang.org/grpc"
    pb "github.com/example/myapp/gen/inference/v1"
)

func callInference(addr string, features []float32) (*pb.PredictResponse, error) {
    conn, err := grpc.Dial(addr, grpc.WithInsecure())
    if err != nil {
        return nil, err
    }
    defer conn.Close()
    client := pb.NewInferenceServiceClient(conn)
    return client.Predict(context.Background(), &pb.PredictRequest{
        ModelId:  "default",
        Features: features,
    })
}
```

### Client side — Kotlin (grpc-kotlin)

```kotlin
// build.gradle.kts: io.grpc:grpc-kotlin-stub
import inference.v1.InferenceServiceGrpcKt
import inference.v1.predictRequest

val channel = ManagedChannelBuilder.forAddress(host, port).usePlaintext().build()
val stub = InferenceServiceGrpcKt.InferenceServiceCoroutineStub(channel)

val response = stub.predict(predictRequest {
    modelId = "default"
    features.addAll(listOf(0.5f, 1.2f, 3.0f))
})
println("${response.label} @ ${response.confidence}")
```

### Python gRPC client (calling Rust or Go gRPC server)

```python
# pip install grpcio grpcio-tools
import grpc
import inference_pb2
import inference_pb2_grpc

def call_inference(addr: str, features: list[float]) -> dict:
    with grpc.insecure_channel(addr) as channel:
        stub = inference_pb2_grpc.InferenceServiceStub(channel)
        response = stub.Predict(inference_pb2.PredictRequest(
            model_id="default",
            features=features,
        ))
        return {"label": response.label, "confidence": response.confidence}
```

### docker-compose.yml snippet

```yaml
services:
  kernel:
    build: ./services/kernel
    ports:
      - "50051:50051"
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:50051"]
      interval: 10s
      timeout: 5s
      retries: 3

  gateway:
    build: ./services/gateway
    environment:
      GRPC_KERNEL_ADDR: kernel:50051
    depends_on:
      kernel:
        condition: service_healthy
```

If `grpc_health_probe` is not available in the image, use an HTTP wrapper:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
```
and expose a `/healthz` HTTP endpoint alongside the gRPC server.

---

## REST/HTTP Seam

Use when one service needs to call another via simple request/response and a human-readable, self-documenting schema is sufficient.

### Server side — Python FastAPI

```python
# pip install fastapi uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    model_id: str
    features: list[float]

class PredictResponse(BaseModel):
    label: str
    confidence: float

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    # run inference
    return PredictResponse(label="positive", confidence=0.91)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
```

FastAPI generates an OpenAPI spec automatically at `/openapi.json`. Commit a snapshot to `docs/seam-contract/inference-openapi.json`.

### Client side — Go (net/http)

```go
import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
)

type PredictRequest struct {
    ModelID  string    `json:"model_id"`
    Features []float64 `json:"features"`
}

type PredictResponse struct {
    Label      string  `json:"label"`
    Confidence float64 `json:"confidence"`
}

func callInference(features []float64) (*PredictResponse, error) {
    baseURL := os.Getenv("INFERENCE_URL") // e.g. http://inference:8000
    body, _ := json.Marshal(PredictRequest{ModelID: "default", Features: features})
    resp, err := http.Post(baseURL+"/predict", "application/json", bytes.NewReader(body))
    if err != nil {
        return nil, fmt.Errorf("inference unavailable: %w", err)
    }
    defer resp.Body.Close()
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("inference returned %d", resp.StatusCode)
    }
    var result PredictResponse
    json.NewDecoder(resp.Body).Decode(&result)
    return &result, nil
}
```

### Node/TypeScript fetch client calling a Go server

```typescript
const GATEWAY_URL = process.env.GATEWAY_URL ?? "http://gateway:8080";

interface RecordPayload { id: string; value: number }
interface RecordResponse { status: string; stored_id: string }

async function submitRecord(payload: RecordPayload): Promise<RecordResponse> {
  const res = await fetch(`${GATEWAY_URL}/records`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`gateway error: ${res.status}`);
  return res.json() as Promise<RecordResponse>;
}
```

### docker-compose.yml snippet

```yaml
services:
  inference:
    build: ./services/inference
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  gateway:
    build: ./services/gateway
    ports:
      - "8080:8080"
    environment:
      INFERENCE_URL: http://inference:8000
    depends_on:
      inference:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### Error handling when downstream is unavailable

The caller must handle downstream unavailability explicitly:
- Return a `503 Service Unavailable` with a structured error body, not a `500`
- Log the downstream error with the correlation ID for tracing
- The `/healthz` endpoint on the caller should return a degraded status when the downstream is unreachable

---

## Port/NIF Seam (Elixir ↔ Rust)

Use when Rust is a hot-path library called from Elixir in the same OS process or via a supervised external process. This seam does not require docker-compose changes — there is no separate Rust container.

### NIF setup — Rust side (Rustler)

```toml
# services/coordinator/native/mylib/Cargo.toml
[package]
name = "mylib"
version = "0.1.0"
edition = "2021"

[lib]
name = "mylib"
crate-type = ["cdylib"]

[dependencies]
rustler = "0.31"
```

```rust
// services/coordinator/native/mylib/src/lib.rs
use rustler::{Encoder, Env, NifResult, Term};

#[rustler::nif]
fn compute_hash(input: &str) -> String {
    // deterministic, non-blocking computation only
    format!("{:x}", md5::compute(input))
}

rustler::init!("Elixir.MyApp.NativeHash", [compute_hash]);
```

### NIF setup — Elixir side (Rustler)

```elixir
# mix.exs
defp deps do
  [
    {:rustler, "~> 0.31", runtime: false},
    # ...
  ]
end
```

```elixir
# lib/my_app/native_hash.ex
defmodule MyApp.NativeHash do
  use Rustler, otp_app: :my_app, crate: "mylib"

  # Stub — replaced by the NIF at runtime
  def compute_hash(_input), do: :erlang.nif_error(:nif_not_loaded)
end
```

Call the NIF:
```elixir
MyApp.NativeHash.compute_hash("hello world")
# => "5eb63bbbe01eeed093cb22bb8f5acdc3"
```

### When to use Port instead of NIF

Use a Port when the Rust code might panic, block, or interact with unsafe external state. A NIF crash takes down the entire BEAM VM. A Port crash is isolated to the OS process; Elixir supervision restarts it.

```elixir
# Port setup — Elixir calls a compiled Rust binary via stdio
defmodule MyApp.KernelPort do
  def start(binary_path) do
    Port.open({:spawn_executable, binary_path}, [
      :binary,
      :exit_status,
      {:packet, 4}   # 4-byte length prefix framing
    ])
  end

  def call(port, payload) do
    encoded = :erlang.term_to_binary(payload)
    send(port, {self(), {:command, encoded}})
    receive do
      {^port, {:data, data}} -> :erlang.binary_to_term(data)
    after
      5_000 -> {:error, :timeout}
    end
  end
end
```

The Rust binary reads from stdin, processes the payload, and writes the result to stdout using the same 4-byte length-prefix framing.

### Notes

- NIFs that block the BEAM scheduler for more than 1ms cause scheduler starvation. Use dirty NIFs (`#[rustler::nif(schedule = "DirtyNif")]`) for any computation that may run longer.
- NIFs that crash kill the entire BEAM VM — use Port for operations involving FFI, raw pointers, or code paths that might panic.
- This seam does not appear in docker-compose because Rust is compiled and loaded in-process or as a sidecar binary alongside the Elixir service.
- Commit the Rust source in `services/coordinator/native/`; do not commit compiled `.so` or `.dll` artifacts.
