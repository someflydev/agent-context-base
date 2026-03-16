# Multi-Backend Coordination

Authoritative rules for systems where two or three backend services in different languages work together to serve a single product capability.

## When to Use Multiple Backends

A multi-backend system is justified only when each language owns a concern where the others would be meaningfully worse. The coordination overhead is real: every seam must be maintained, every local dev session spins up multiple containers, and every deployment has more moving parts.

Decision heuristic: ask whether the gain from each language owning its concern exceeds the cost of seam maintenance, local dev complexity, and deployment ops. The bar is real. If one language can do the job well enough, don't split.

Signs the split is justified:
- One service does ML inference and the other handles high-throughput API routing — different performance profiles, different dependency trees
- One service owns fault-tolerant distributed state and the other does CPU-bound computation — different runtime guarantees
- One service is an existing JVM platform service and the new work genuinely belongs in a systems language

Signs the split is not justified:
- "We want to learn both languages" — use polyglot-lab archetype instead
- "The second service might be useful someday" — build it when it's needed
- Both services would share the same database schema and coordinate writes — this is one service wearing two hats

## Ownership Model

Every service in a multi-backend system must have a one-sentence ownership statement that names what it owns and why that language earns the assignment.

Pattern: `{Service name} ({language}): owns {concern} because {language-specific justification}.`

Examples:
- `gateway (Go): owns HTTP routing, rate limiting, and auth because Go's concurrency model handles connection volume without GC pauses.`
- `inference (Python): owns ML model serving because the model is PyTorch and the ecosystem is Python-native.`
- `coordinator (Elixir): owns distributed job scheduling and fault recovery because the BEAM provides supervisor trees and per-process isolation.`
- `kernel (Rust): owns codec and cryptographic hot paths because Rust provides zero-cost abstractions and memory safety without a runtime.`

Language ownership reference:
- **Go**: high-throughput networking, API gateway, ops tooling, service mesh glue
- **Elixir**: distributed coordination, fault-tolerant supervision, real-time pub/sub, long-lived connections
- **Python**: ML/AI inference, data science pipelines, scripting, batch jobs
- **Rust**: CPU-bound hot paths, systems work, WASM modules, codec/crypto kernels
- **Clojure**: rich data transformation, business rule engines, Kafka Streams processing
- **Kotlin**: JVM ecosystem services, Spring/Ktor services, Android platform backends
- **Scala**: distributed streaming (Akka/Spark), batch analytics, actor-model coordination
- **Node/TypeScript**: BFF layer, real-time WebSocket/SSE, GraphQL subscriptions

Anti-patterns:
- Two services both described as "handling business logic" — ownership conflict; one of them is wrong
- Two services both "owning the user entity" — shared ownership is no ownership; pick one
- A service described as "the general-purpose backend" — this is a seam problem disguised as architecture


## Seam Types

The only interface between two services is their seam. Choose exactly one seam type per service pair. If a pair seems to need two protocols, the ownership boundary is not well-defined.

### Broker Seam (async, decoupled)

**Technology:** NATS JetStream (lightweight), Kafka (high-throughput, schema registry)
**Direction:** producer → broker → consumer(s)
**Best for:** one service produces events that one or more others consume independently; fan-out patterns; fire-and-forget writes; strict decoupling required
**Schema contract:** event schema defined in the broker subject/topic spec; include `payload_version`, `correlation_id`, `published_at` in every payload
**Anti-pattern:** using a broker for synchronous request/response loops — adds latency and complexity without benefit

### gRPC Seam (synchronous, typed)

**Technology:** Protocol Buffers + gRPC
**Direction:** caller → server (unary or streaming RPC)
**Best for:** synchronous results required (ML inference call, compute kernel result); strong schema enforcement across language boundaries; performance matters for the call itself
**Schema contract:** `.proto` file is the canonical contract; both sides generate client/server stubs from it; the proto file lives in `docs/seam-contract/`
**Anti-pattern:** using gRPC when REST would suffice (adds proto ceremony); versioning neglect (breaking changes without field deprecation)

### REST/HTTP Seam (synchronous, self-documenting)

**Technology:** HTTP + JSON (or msgpack for binary-heavy payloads)
**Direction:** caller → server (request/response)
**Best for:** simple request/response; human-readable schema is sufficient; one service is already a public API; no streaming needed
**Schema contract:** OpenAPI spec or equivalent; JSON schema validation at boundary; FastAPI generates `/openapi.json` automatically
**Anti-pattern:** REST for high-frequency tight loops (use gRPC); undocumented schemas drifting from implementation

### Port/NIF Seam (in-process, Elixir-specific)

**Technology:** Elixir NIF (native implemented function via Rustler) or Port (external OS process)
**Direction:** Elixir calls into Rust library within the same OS process or via a pipe
**Best for:** Rust is a hot-path library, not an independent service; sub-millisecond latency required; network overhead is unacceptable
**Schema contract:** Erlang term format or binary at the NIF boundary; document the input/output term shapes explicitly
**Anti-pattern:** NIFs that panic or block the BEAM scheduler (a panicking NIF kills the VM); use Port for code that might be unsafe

### Seam Selection Heuristic

| Need | Preferred seam |
|---|---|
| ML inference call, synchronous result required | gRPC |
| Fan-out events to multiple consumers | Broker (NATS or Kafka) |
| Simple API delegation, human-readable schema | REST |
| Hot-path compute in same OS process as Elixir | NIF/Port |
| BFF calling internal services | REST or gRPC |
| Business rules engine returning a result | gRPC or REST |
| High-throughput event stream, schema registry needed | Broker (Kafka) |
| Lightweight event bus for local dev and small volumes | Broker (NATS) |


## No Shared Database

Two services in different languages must not write to the same database schema.

**Acceptable:**
- Service A writes to its own schema; Service B reads from a published API or event stream produced by Service A
- Both services read (but only one writes) a shared read-replica — the writing service owns the schema

**Not acceptable:**
- Service A and Service B both write to the same Postgres schema or the same MongoDB collection without an intermediary
- Using a shared cache (Redis) as a coordination mechanism with writes from both services and no clear owner

**Preferred alternatives when a shared read model is genuinely needed:**

Event sourcing: Service A publishes events to the broker; Service B maintains its own read projection from those events. The projection is owned by Service B and can be rebuilt from the event log.

API delegation: Service B calls Service A's API to read the data. Service A remains the authoritative owner; Service B does not persist a copy.


## Health Contract

Every service must expose a health endpoint at a canonical path:
- HTTP services: `GET /healthz` returning `200 OK` with `{"status": "ok"}`
- gRPC services: `grpc.health.v1.Health/Check` (standard gRPC health protocol)
- Elixir NIF/Port services: supervision strategy or a Port heartbeat that Elixir monitors

`docker-compose.yml` must declare:
- `healthcheck:` for each service with a meaningful test command
- `depends_on:` with `condition: service_healthy` where services must be ready before their dependents start

Failure propagation must be explicit. If Service A calls Service B and Service B fails, Service A's health check must degrade predictably — return a `503` or a degraded status — rather than crashing with an unhandled connection error. Do not treat cross-service errors as unexpected.

Example healthcheck block:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 15s
```


## Local Dev Composition

Each service runs in its own container. The `docker-compose.yml` declares all services with:
- Explicit port bindings (no implicit port sharing)
- Health checks for each service
- `depends_on` with `condition: service_healthy` where startup order matters
- Environment variables providing seam addresses (`NATS_URL`, `INFERENCE_SERVICE_URL`, `GRPC_KERNEL_ADDR`)
- No hardcoded IPs; use Docker service names as hostnames

`docker-compose.test.yml` is a separate file for isolated integration test runs. It may use different ports, ephemeral volumes, and stripped-down service configurations. Keep it distinct from the dev composition.

Environment variable pattern:
```yaml
environment:
  INFERENCE_URL: http://inference:8000
  NATS_URL: nats://nats:4222
  GRPC_KERNEL_ADDR: kernel:50051
```


## Deployment Model

Three patterns in order of operational simplicity:

**1. Separate Dokku apps** (each service deployed independently, connected by URL)
- Best for: duos where each service has independent scaling and release cycles
- Services discover each other via environment variables set in Dokku config
- Preferred when services have different resource profiles (e.g., a GPU-enabled Python inference service vs. a Go gateway)

**2. Single docker-compose on a single host** (all services co-located)
- Best for: trios and early-stage duos where operational simplicity matters more than independent scaling
- All services share the host network; seam addresses use Docker service names
- Simplest ops path; deploy the compose file, pull images, restart

**3. Kubernetes** (when scale requires it)
- Out of scope for this repo
- Consider when independent horizontal scaling per service is required and the team has Kubernetes operational capacity

Deployment pattern preference by system type:
- Duo with independent scaling profiles → separate Dokku apps
- Duo or trio on one host, same release cadence → docker-compose on a single host
- Trio with heterogeneous resource needs → separate Dokku apps or Kubernetes


## Failure Modes

**Domain bleed:** a service doing work that belongs to another service. Symptom: ownership statements start overlapping. Fix: clarify ownership and move the code.

**Seam proliferation:** two or more protocols between the same service pair. Symptom: one service calls another via both REST and a broker topic. Fix: pick one; the seam is the contract.

**Shared database:** direct DB writes from two services to one schema. Symptom: both services import each other's ORM models or share a migration directory. Fix: apply the no-shared-database rule; use events or API delegation.

**Missing health checks:** silent failure propagation across the seam. Symptom: a downstream service fails but the upstream doesn't degrade or surface an error. Fix: implement `/healthz` on all services and add `depends_on: condition: service_healthy` in compose.

**Synchronous where async would suffice:** unnecessary coupling created by a sync seam. Symptom: a gRPC or REST call blocks the caller waiting for a result that doesn't need to be immediate. Fix: convert to a broker event if the caller can proceed without the result.

**NIF panic:** a Rust NIF crashes, taking down the entire BEAM VM. Symptom: the Elixir node crashes on certain inputs. Fix: use an Elixir Port instead of a NIF for code that might panic; NIFs are only appropriate for provably safe, non-blocking Rust functions.


## Related

- `context/archetypes/multi-backend-service.md`
- `context/workflows/design-multi-backend-seams.md`
- `context/workflows/add-backend-coordination-layer.md`
- `context/stacks/coordination-seam-patterns.md`
