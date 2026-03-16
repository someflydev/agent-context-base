# Seam: Elixir + Rust NIF/Port (in-process)

## Why There Is No docker-compose.yml

This example has no `docker-compose.yml` because the NIF seam is **in-process** — not a two-service system.

The Rust crate (`native/compute_nif/`) is compiled by Rustler during `mix compile` and produces a shared library (`.so` on Linux, `.dylib` on macOS, `.dll` on Windows). That library is loaded directly into the BEAM VM at application startup. When Elixir calls `MyApp.ComputeNif.compute_hash/1`, the call crosses from the Erlang scheduler into native Rust code within the same OS process — with no network hop, no serialization overhead, and no container boundary.

This is the most architecturally unique seam type in the repo. All other seam examples involve two processes communicating over a network. This one is a library call.

## Setup (Replaces docker-compose for This Example)

### 1. Prerequisites

Install the Rust toolchain:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup toolchain install stable
```

### 2. Add Rustler to mix.exs

```elixir
# mix.exs
defp deps do
  [
    {:rustler, "~> 0.31", runtime: false},
    # ... other deps
  ]
end
```

`runtime: false` means Rustler is a build-time dependency only — it is not bundled into the runtime release after compilation.

### 3. Place Rust source files

```
my_app/
  native/
    compute_nif/
      Cargo.toml      ← from this example (Cargo.toml)
      src/
        lib.rs        ← from this example (rust-nif.rs)
  lib/
    my_app/
      compute_nif.ex  ← from this example (elixir-host.ex)
  mix.exs
```

### 4. Build

```bash
mix deps.get
mix compile   # Rustler invokes `cargo build` for the NIF crate automatically
```

On first build, Cargo downloads and compiles Rustler's dependencies — expect 1–2 minutes. Subsequent builds are incremental.

### 5. Verify in IEx

```bash
iex -S mix
```

```elixir
iex> MyApp.ComputeNif.compute_hash("hello world")
{:ok, "b6a4f9d2..."}

iex> MyApp.ComputeNif.normalize_vector([1.0, 2.0, 3.0])
{:ok, [0.0, 0.5, 1.0]}

iex> MyApp.ComputeNif.normalize_vector([5.0, 5.0, 5.0])
{:ok, [0.0, 0.0, 0.0]}
```

### 6. Run tests

```bash
mix test
```

---

## Why NIF, Not Port, Not a Separate Service

| Option | When to use | Trade-off |
|---|---|---|
| **NIF (Rustler)** | Sub-millisecond latency required; Rust code is well-tested and will not panic | A NIF panic kills the entire BEAM VM; no process isolation |
| **Port** | Rust code might panic, block, or interact with unsafe state | Isolated OS process; Elixir supervisor can restart on crash; ~10–50µs IPC overhead per call |
| **Separate gRPC/REST service** | Rust is an independent service, not a library; different scaling or deployment lifecycle | Network hop; container orchestration; service health management |

Choose NIF when:
- The latency budget is under 1ms and the network overhead of a service call is unacceptable.
- The Rust code is small, well-tested, and unlikely to panic (pure compute: hashing, vector math, compression, codec operations).
- The BEAM process model and supervision tree own the retry/recovery logic — Rust just does the computation.

Choose Port when:
- The Rust code is experimental, uses unsafe FFI, calls into external C libraries, or has code paths that might panic.
- You cannot afford a full VM crash if the Rust code misbehaves.

The Port variant for the same two functions:

```elixir
defmodule MyApp.ComputePort do
  def start(binary_path) do
    Port.open({:spawn_executable, binary_path}, [
      :binary,
      :exit_status,
      {:packet, 4}   # 4-byte length-prefix framing
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

The Rust binary for Port mode reads from stdin and writes to stdout using the same 4-byte length-prefix framing. See `context/stacks/coordination-seam-patterns.md#port-nif-seam` for the full Port pattern.

---

## NIF Safety Rules

> **A NIF that panics kills the entire BEAM VM.** There is no process isolation at the NIF boundary. If `compute_hash` panics, the Elixir application crashes entirely — not just the calling process.

Rules (summarized from `context/stacks/coordination-seam-patterns.md`):

1. **Do not block the BEAM scheduler for more than 1ms.** Use `#[rustler::nif(schedule = "DirtyCpu")]` for any computation that may run longer. Without this annotation, a slow NIF starves the BEAM scheduler and degrades the entire application.

2. **Do not panic inside a NIF.** Use `std::panic::catch_unwind` if there is any risk, or switch to Port. A panic in a NIF is an unrecoverable VM crash.

3. **Do not call other NIFs or Erlang functions from inside a NIF.** This can deadlock the scheduler.

4. **Do not allocate unbounded memory in a NIF.** Large NIF allocations are invisible to BEAM's garbage collector and can cause the VM to run out of memory without warning.

---

## Observing the Seam

Run the tests to confirm the NIF loads and returns correct values:

```bash
mix test
```

Example test (ExUnit):

```elixir
defmodule MyApp.ComputeNifTest do
  use ExUnit.Case

  test "compute_hash returns ok tuple with hex string" do
    assert {:ok, hash} = MyApp.ComputeNif.compute_hash("test input")
    assert is_binary(hash)
    assert String.match?(hash, ~r/^[0-9a-f]+$/)
  end

  test "normalize_vector maps to [0.0, 1.0]" do
    assert {:ok, [0.0, 0.5, 1.0]} = MyApp.ComputeNif.normalize_vector([1.0, 2.0, 3.0])
  end

  test "normalize_vector handles all-equal values" do
    assert {:ok, [0.0, 0.0, 0.0]} = MyApp.ComputeNif.normalize_vector([5.0, 5.0, 5.0])
  end

  test "normalize_vector handles empty list" do
    assert {:ok, []} = MyApp.ComputeNif.normalize_vector([])
  end
end
```

---

## Dockerfile Pattern (Production)

For production builds, compile the NIF in a multi-stage Dockerfile:

```dockerfile
FROM rust:1.82-slim AS rust-builder
WORKDIR /build
COPY native/ ./native/
RUN cd native/compute_nif && cargo build --release

FROM elixir:1.17-otp-27 AS app
WORKDIR /app
COPY --from=rust-builder /build/native/compute_nif/target/release/libcompute_nif.so priv/native/
COPY mix.exs mix.lock ./
RUN mix deps.get --only prod
COPY . .
RUN mix release
CMD ["/app/_build/prod/rel/my_app/bin/my_app", "start"]
```

Do not commit compiled `.so` or `.dll` artifacts — compile them during the Docker build.

---

## Related

- `context/stacks/duo-elixir-rust.md` — Elixir + Rust duo stack doc
- `context/stacks/coordination-seam-patterns.md` — full Port/NIF pattern with safety rules
- `context/stacks/elixir-phoenix.md` — Elixir stack reference
- `context/stacks/rust-axum-modern.md` — Rust stack reference
