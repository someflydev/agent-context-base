# Canonical Schema Validation Examples

## Purpose

This directory is the shared comparison surface for schema-validation examples
across seven languages and three lanes: Lane A for runtime validation, Lane B
for contract generation, and Lane C for hybrid type-driven flows. Every example
uses the same WorkspaceSyncContext domain and the same fixture corpus so the
comparison is about library behavior rather than mismatched problem choices.
That shared baseline makes validation ergonomics, schema export, and parity
rules comparable across ecosystems.

## Domain

The domain is `WorkspaceSyncContext`. It models a workspace-scoped sync system
with five canonical models:

- `WorkspaceConfig` configures workspace limits, ownership, and settings.
- `SyncRun` records the lifecycle and outcome of a sync execution.
- `WebhookPayload` captures emitted events with discriminated event data.
- `IngestionSource` describes registered upstream source connections.
- `ReviewRequest` represents review workflows tied to synchronized content.

Authoritative domain spec: [domain/models.md](domain/models.md)

## Languages and Libraries

| Language | Lane A (Runtime) | Lane B (Contract) | Lane C (Hybrid) |
| --- | --- | --- | --- |
| Python | Pydantic, marshmallow | Pydantic model_json_schema() | Pydantic |
| TypeScript | Zod, Valibot, io-ts | TypeBox + Ajv | Zod, io-ts |
| Go | go-playground/validator, ozzo-validation | External tooling (swaggo, kin-openapi) | — |
| Rust | validator, garde | serde + schemars | — |
| Kotlin | Konform, Hibernate Validator | SpringDoc / kotlinx.serialization | — |
| Ruby | dry-validation, dry-schema | dry-schema JSON Schema output | — |
| Elixir | Ecto.Changeset, Norm | ex_json_schema | — |

## Fixture Corpus

The shared JSON corpus lives under [domain/fixtures/](domain/fixtures/). Valid
fixtures must pass in every implementation, invalid fixtures must be rejected
in every implementation, and edge fixtures are where documented language and
library differences are allowed. Those edge differences are tracked in
`PARITY.md`, not hidden in example-specific behavior.

## Navigation

- [CATALOG.md](CATALOG.md) — full inventory of all examples by status
- [PARITY.md](PARITY.md) — cross-language consistency rules and documented divergences
- [domain/models.md](domain/models.md) — language-agnostic model spec
- [domain/fixtures/](domain/fixtures/) — shared JSON payload corpus

## Verification

Fixture corpus verification lives in
[`verification/schema-validation/`](../../verification/schema-validation/).
The first shared entry point is
`python3 -m unittest discover -s verification/schema-validation -p "test_*.py" -v`.
Language-specific smoke tests will be added alongside the examples in
PROMPT_115 through PROMPT_117.
