# Duo: Elixir + Rust

Elixir and Rust combine to form a media or compute platform where Elixir supervises distributed job execution and Rust performs the CPU-bound transformation inline — audio/video transcoding, cryptographic operations, binary parsing, or compression — without the network overhead of a separate service. This is not a two-service system: Rust is compiled as a native library loaded directly into the BEAM VM via a NIF (Rustler) or invoked as a supervised external process via a Port. Elixir owns the process model, retry logic, and API surface; Rust owns the hot compute path.

## Division of Labor

| Responsibility | Owner |
|---|---|
| API surface, job scheduling, retry and recovery | Elixir |
| Distributed process supervision (OTP) | Elixir |
| CPU-bound compute: codec, crypto, compression, parsing | Rust |
| NIF/Port lifecycle and crash isolation | Elixir |
| Client-facing real-time updates (LiveView, Channels) | Elixir |
| Seam contract | Both |

## Primary Seam

NIF/Port seam: Elixir calls Rust functions within the same OS process (NIF via Rustler) or through a supervised Port (external binary); Rust returns an Erlang term or binary result synchronously.

## Communication Contract

NIF call shape (Rustler):
```elixir
# Calling the Rust NIF from Elixir
MyApp.NativeCodec.transcode(binary_data, %{format: :h264, bitrate: 1_500_000})
# => {:ok, transcoded_binary}
# => {:error, "unsupported input format"}
```

Port call shape (4-byte length-prefix framing, Erlang terms):
```elixir
# Elixir sends payload; Rust binary reads from stdin and writes to stdout
payload = {:transcode, input_binary, [format: :h264]}
encoded = :erlang.term_to_binary(payload)
# Port receives and returns:
# {:ok, result_binary}
# {:error, reason_string}
```

Rust NIF signature (Rustler):
```rust
#[rustler::nif(schedule = "DirtyCpu")]
fn transcode(input: Binary, opts: TranscodeOpts) -> NifResult<OwnedBinary> {
    // CPU-bound work on a dirty scheduler thread — does not block the BEAM
    ...
}
```

Use `DirtyCpu` for any computation that may exceed 1ms to avoid BEAM scheduler starvation.

## Local Dev Composition

This duo compiles to a single service — Rust is linked into the Elixir release. There is no separate Rust container.

```yaml
services:
  elixir-app:
    build:
      context: ./services/app
      dockerfile: Dockerfile
      # Dockerfile uses elixir:1.17-otp-27 base image;
      # Rust toolchain (rust:1.82) is installed in a multi-stage build
      # to compile the NIF before assembling the Elixir release.
    ports:
      - "4000:4000"
    environment:
      PHX_HOST: localhost
      PORT: "4000"
      SECRET_KEY_BASE: dev-secret-replace-in-prod
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 25s
```

Multi-stage Dockerfile pattern:
```dockerfile
FROM rust:1.82-slim AS rust-builder
WORKDIR /build
COPY native/ ./native/
RUN cd native/mylib && cargo build --release

FROM elixir:1.17-otp-27 AS app
WORKDIR /app
COPY --from=rust-builder /build/native/mylib/target/release/libmylib.so priv/native/
COPY mix.exs mix.lock ./
RUN mix deps.get --only prod
COPY . .
RUN mix release
CMD ["/app/_build/prod/rel/app/bin/app", "start"]
```

## Health Contract

- **elixir-app**: `GET /healthz` → `200 {"status":"ok"}` via Phoenix router
- NIF health is implicit: if the NIF crashes, the BEAM VM crashes — use Ports for untrusted code paths
- Port health: Elixir supervisor monitors the Port process; restart policy defined in the supervision tree

## When to Use This Duo

- Media platforms requiring inline transcoding or encoding where spawning a separate service adds unacceptable latency.
- Cryptographic operations (key derivation, signing, verification) that must be fast and memory-safe, called from Elixir without a network hop.
- Binary parsing or compression in a hot path — e.g., parsing incoming binary protocol frames before routing them through OTP processes.
- Platforms that want the BEAM's fault tolerance and supervision model with Rust performance for a specific bounded computation.
- Scenarios where a network round-trip to a gRPC service would add more latency than the computation itself takes.

## When NOT to Use This Duo

- The compute task is I/O-bound rather than CPU-bound — a pure Elixir GenServer or Task is sufficient.
- The Rust code is experimental or not well-tested for safety — use a Port (not a NIF) if there is any risk of panics; or keep Rust as a separate gRPC service until stability is proven.
- The team does not have Rust expertise — the NIF boundary is low-level; a mistake can crash the entire VM. Consider Elixir + Go (REST seam) as a safer alternative for teams new to Rust.

## Related

- context/doctrine/multi-backend-coordination.md
- context/stacks/elixir-phoenix.md
- context/stacks/rust-axum-modern.md
- context/stacks/coordination-seam-patterns.md
