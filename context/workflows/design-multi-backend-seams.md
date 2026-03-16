# Design Multi-Backend Seams

## Purpose

Decide service ownership boundaries and seam type before writing code. This workflow produces the design artifacts that `add-backend-coordination-layer.md` consumes. Run this workflow first — implementing a seam before ownership is clear creates rework.

## When to Use It

- Starting a multi-backend project (duo or trio)
- Adding a third service to an existing two-service system
- Refactoring a seam that has grown too complex or has multiple protocols between the same pair

## Sequence

1. **Write ownership statements.** For each language in the system, write one sentence: `{Service name} ({language}): owns {concern} because {language-specific justification}.` Stop if two statements overlap — resolve the ownership conflict before proceeding. Two services that both "handle business logic" or both "own the user entity" signal a seam problem, not an implementation detail.

2. **Identify the communication pattern for each service pair.** For each pair, answer:
   - Does the caller need a synchronous result? → gRPC or REST
   - Does the producer need fire-and-forget delivery to one or more consumers? → Broker
   - Is one service a Rust library called from Elixir in the same process? → NIF or Port

3. **Apply the seam selection heuristic.** Consult the selection table in `context/doctrine/multi-backend-coordination.md`. Choose exactly one seam type per service pair. If the pattern seems to require two protocols between the same pair, revisit the ownership statements — the boundary is not clean.

4. **Define the schema contract for each seam.** Write the contract artifact before writing application code:
   - gRPC seam → write the `.proto` file first; both sides generate stubs from it
   - Broker seam → write the event schema as a JSON Schema file or annotated example payload; include `payload_version`, `correlation_id`, `published_at`
   - REST seam → write the OpenAPI endpoint spec or a `curl` + response example
   - NIF/Port seam → document the Erlang term shape at the boundary (input type, output type, error cases)

5. **Draw the ownership and seam diagram.** Even an informal sketch counts. Each node is a service labeled with its language; each edge is labeled with the seam type and primary subject/path. For a gRPC seam: `gateway (Go) --[gRPC: /inference.v1.Inference/Predict]--> inference (Python)`. For a broker seam: `pipeline (Go) --[NATS: events.ingested.>]--> coordinator (Elixir)`.

6. **Write the architecture doc.** Produce `docs/architecture.md` (or equivalent). Include: ownership table, seam diagram, seam contracts (or links to them in `docs/seam-contract/`), health contract per service.

## Outputs

- Ownership table: one row per service (name, language, one-sentence responsibility)
- Seam contract for each service pair (`.proto`, event schema, or OpenAPI snippet)
- docker-compose topology sketch: which service depends on which; which needs a broker service
- `docs/architecture.md` draft with the above artifacts

## Stop Conditions

- Every service has an unambiguous, non-overlapping ownership statement
- Every service pair has exactly one seam type documented
- No shared database planned
- Health contract defined for each service (endpoint path or supervision strategy)
- Schema contract artifact exists in `docs/seam-contract/` for each seam

## Common Pitfalls

- **Designing the seam before resolving ownership:** premature infrastructure choice. Finish the ownership table first.
- **Choosing gRPC for everything:** adds proto ceremony and stub generation when REST would suffice for simple delegation.
- **Designing for a trio when a duo is sufficient:** start with the minimum that justifies the coordination overhead; add the third service when the need is real.
- **Picking the seam before knowing the access pattern:** a caller that needs a synchronous result cannot use a broker seam without adding a correlation ID round-trip hack. Determine sync vs. async first.
- **Skipping the schema contract:** proceeding to implementation without a proto, schema, or OpenAPI spec means both sides will drift independently.
