# Add Backend Coordination Layer

## Purpose

Implement the seam between two services once ownership and seam type are decided. Run `design-multi-backend-seams.md` before this workflow — the outputs of that workflow are the inputs here.

## When to Use It

- After completing `design-multi-backend-seams.md`
- Adding a seam to an existing service pair that previously had no formal coordination layer
- Replacing an informal side channel (shared DB, shared filesystem) with an explicit seam

## Sequence

1. **Scaffold each service directory.** Create `services/{service-a}/` and `services/{service-b}/` (and `services/{service-c}/` for a trio). Each directory gets its own `Dockerfile` and entry point. Follow the language's stack doc for internal structure. Do not share source directories across services.

2. **Add seam infrastructure to `docker-compose.yml`.** The infrastructure needed depends on the seam type:
   - Broker seam (NATS): add a `nats` service with `-js` flag; expose ports `4222` and `8222`
   - Broker seam (Kafka): add `zookeeper` and `kafka` services; expose the broker port
   - gRPC seam: no extra service; expose the gRPC port from the server service in the compose file
   - REST seam: no extra service; expose the HTTP port from the server service
   - NIF/Port seam: no extra service; Rust is compiled into or alongside the Elixir service

3. **Implement the schema contract.** Use the contract artifact from `docs/seam-contract/` as the source of truth:
   - gRPC: run `protoc` to generate client and server stubs for each language from the `.proto` file; commit generated stubs or the generation command to the repo
   - Broker: implement stream/consumer creation and publish/subscribe helpers in each service; validate payload shape against the event schema on the subscriber side
   - REST: implement the endpoint in the server service following the OpenAPI spec; implement the client call in the caller using the same spec
   - NIF: compile the Rust crate as a NIF using Rustler; add `{:rustler, ...}` to `mix.exs`; define the NIF stub module in Elixir
   - Port: compile the Rust binary separately; open the Port in Elixir with `Port.open({:spawn_executable, path}, [:binary])`

4. **Add health checks to `docker-compose.yml`.** Every service needs a `healthcheck:` block. Add `depends_on:` with `condition: service_healthy` so dependent services wait for their upstreams. Do not skip this step — boot order without health conditions is unpredictable.

5. **Write a smoke test for the seam.** The test must:
   - Bring up the full composition (or the relevant services)
   - Trigger one request or event from the caller side
   - Assert the receiving service handles it correctly (check a response, a DB write, a logged output)
   - Assert `/healthz` returns `200` on both services after the round-trip

6. **Commit the seam contract to the repo.** The `.proto` file, event schema, or OpenAPI spec must be committed to `docs/seam-contract/`. The contract is not "in memory" — it is a versioned artifact that both services depend on.

## Outputs

- `services/{service-a}/` and `services/{service-b}/` scaffolds with Dockerfiles and entry points
- `docker-compose.yml` with both services, health checks, seam infrastructure, and `depends_on` conditions
- Seam contract files committed to `docs/seam-contract/`
- Smoke test covering one round-trip across the primary seam path

## Stop Conditions

- `docker-compose up` starts all services and all health checks pass
- One smoke test exercises the primary seam path end-to-end
- Seam contract artifact is committed to the repo
- No service address is hardcoded; all cross-service addresses come from environment variables

## Common Pitfalls

- **Building application logic before the seam smoke test passes:** if the seam doesn't work, application logic is untestable. Get the health check and one round-trip working first.
- **Hardcoding service addresses:** use environment variables (`INFERENCE_URL`, `NATS_URL`, `GRPC_KERNEL_ADDR`) injected by docker-compose; hardcoded IPs or ports break in different environments.
- **Skipping health checks:** without `condition: service_healthy`, a dependent service starts before its upstream is ready and fails with a connection error that looks like an application bug.
- **Implementing both directions of the seam simultaneously:** implement the server side first, smoke test it independently, then implement the client side. Doing both at once makes debugging harder.
- **Not committing the schema contract:** a proto or event schema that lives only in one developer's head (or in generated stubs without the source) will drift. Commit the canonical source artifact.
