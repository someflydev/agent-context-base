# Multi-Backend Service

Use this archetype for repos where two or three backend services in different languages coordinate to serve a single product capability.

## When to Use This Archetype

The project explicitly assigns non-overlapping responsibilities to 2–3 language runtimes. The coordination seam is designed, not accidental. Each service would be awkward or slow if implemented in one of the other languages.

Contrast with:
- **polyglot-lab**: exploratory, no production coordination seam required, each surface is independent
- **backend-api-service**: single deployable service in one language, may depend on external storage or queues

This archetype is appropriate when:
- Each language owns a distinct concern that the others cannot serve as well
- The services must be deployed and operated as a coordinated system, not independently
- The seam between services is an explicit design decision, not an accidental shared dependency

This archetype is not appropriate when:
- One language can serve the full capability well enough
- The goal is exploration rather than production coordination
- The services share a database schema and coordinate writes without an intermediary

## Repo Structure

```
services/
  {service-a}/         # owns its own Dockerfile, deps, and tests
    Dockerfile
    src/
    tests/
  {service-b}/         # same pattern
    Dockerfile
    src/
    tests/
  {service-c}/         # if trio; omit if duo
    Dockerfile
    src/
    tests/
docker-compose.yml     # full composition for local dev
docker-compose.test.yml  # isolated test composition
docs/
  architecture.md      # ownership table + seam diagram
  seam-contract/       # proto files, event schemas, OpenAPI specs
```

Each service directory is self-contained. It must have its own `Dockerfile`, its own dependency manifest (`go.mod`, `mix.exs`, `pyproject.toml`, `Cargo.toml`, etc.), and its own test suite. No shared source directories across services.

The `docs/seam-contract/` directory holds the canonical schema artifacts for each seam:
- gRPC seam: `.proto` files
- Broker seam: event schema files (JSON Schema or annotated example)
- REST seam: OpenAPI spec or equivalent

## Required Context

- `context/doctrine/multi-backend-coordination.md` — rules that govern the entire system
- `context/doctrine/compose-port-and-data-isolation.md` — port and data isolation rules for docker-compose
- `context/doctrine/testing-philosophy.md` — test posture for cross-service boundaries
- Stack doc for each service's language (e.g., `context/stacks/go-echo.md`, `context/stacks/rust-axum-modern.md`)
- The relevant duo or trio stack doc when available (from `context/stacks/`)

## Common Workflows

- `context/workflows/design-multi-backend-seams.md` — run this first, before writing any code
- `context/workflows/add-backend-coordination-layer.md` — implement the seam after ownership is decided
- `context/workflows/add-smoke-tests.md` — verify the seam path with a real round-trip

## Typical Anti-Patterns

- **Shared database across services:** two services writing to the same schema; see `context/doctrine/multi-backend-coordination.md` for acceptable alternatives
- **Two seam types between the same pair:** REST and a broker topic between the same two services; pick one; the seam is the contract
- **Ownership drift:** one service doing work clearly belonging to another; re-read ownership statements when this is suspected
- **docker-compose without health checks:** boot order becomes unpredictable; downstream services start before upstreams are ready
- **Collapsing services to avoid coordination overhead:** if the coordination cost seems too high, reconsider whether the split is justified — don't deploy two services as one process to skip the seam
