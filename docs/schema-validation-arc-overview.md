# Schema Validation and Contract Generation Arc

## Purpose

This arc gives assistants and developers a stable way to compare schema
validation libraries across seven languages without collapsing distinct tool
behaviors into one vague category. Cross-language comparison only works when
every example implements the same domain and exercises the same shared fixture
corpus, so this arc standardizes both. The three-lane model matters because
runtime validation, machine-readable contract generation, and hybrid
type-driven workflows answer different engineering questions. After working
through this arc, a developer should be able to choose the right lane, the
right library, and the right example for a validation or contract task.

## The Three Lanes

### Lane A — Runtime Validation

Lane A validates live values against constraints at execution time. It answers
questions about boundary rejection, coercion, nested rules, and cross-field
checks. Lane A may enforce richer rules than a schema exporter can express,
but it does not inherently publish a machine-readable contract. Error shape and
error text remain library-defined.

Libraries by language:

| Language | Primary | Secondary |
| --- | --- | --- |
| Python | Pydantic | marshmallow |
| TypeScript | Zod | Valibot, io-ts |
| Go | go-playground/validator | ozzo-validation |
| Rust | validator | garde |
| Kotlin | Konform | Hibernate Validator |
| Ruby | dry-validation | dry-schema |
| Elixir | Ecto.Changeset | Norm |

### Lane B — Contract Generation

Lane B produces machine-readable schema artifacts for interoperability. The
contract may come from the same definition that validates data, or from a
separate library that only models wire shape. This lane matters when another
service, team, or code generator depends on a JSON Schema or OpenAPI surface.
In Rust especially, contract generation is intentionally separate from runtime
validation: `schemars` exports contracts, while `validator` or `garde` enforce
runtime constraints.

Libraries by language:

| Language | Approach |
| --- | --- |
| Python | Pydantic `model_json_schema()` |
| TypeScript | TypeBox + Ajv (schema is JSON Schema natively) |
| Go | swaggo annotations / external tooling (ergonomic gap) |
| Rust | serde + schemars (contract lane, not validator) |
| Kotlin | SpringDoc / kotlinx.serialization + tooling |
| Ruby | dry-schema JSON Schema output |
| Elixir | ex_json_schema |

### Lane C — Hybrid Type-Driven Flows

Lane C uses one definition surface for three jobs: type, runtime validator, and
schema source. This is the most teaching-friendly lane because one construct
shows the whole relationship between model, validation, and contract export.
It is strongest in Python and TypeScript. Most other ecosystems separate those
responsibilities more explicitly and therefore do not have a dominant hybrid
lane.

| Language | Library | Notes |
| --- | --- | --- |
| Python | Pydantic | `BaseModel`: type = validator = schema source |
| TypeScript | Zod | `z.object(...)` -> infer + parse + JSON Schema export |
| TypeScript | io-ts | Codec: type + decode/encode, FP-oriented |
| Others | — | No mainstream hybrid lane in this arc |

## The WorkspaceSyncContext Domain

WorkspaceSyncContext models a workspace-scoped sync system with configuration,
runtime jobs, webhook events, source registration, and review escalation. It
was chosen because it forces every language example to handle nested objects,
enums, discriminated unions, nullable fields, and cross-field rules in the same
small domain. That shared pressure makes library differences visible without
requiring a large application. The five models are:

- `WorkspaceConfig` — workspace identity, plan, limits, settings, and tags;
  exercises nested objects, enums, timestamps, and plan-tier cross-field rules
- `SyncRun` — runtime execution status and timing; exercises nullable fields,
  status-driven rules, and timestamp ordering
- `WebhookPayload` — event envelope plus variant payload; exercises
  discriminated unions, enum dispatch, and signature format checks
- `IngestionSource` — source registration plus source-type-specific config;
  exercises discriminated unions and source-specific requirements
- `ReviewRequest` — reviewer routing and escalation metadata; exercises list
  uniqueness, optional notes, and priority-driven due-date rules

## Key Distinctions to Preserve

- `serde + schemars` in Rust is Lane B, not Lane A. `serde` defines wire shape,
  `schemars` exports schema, and `validator` or `garde` enforce constraints.
- `io-ts` is not a simpler Zod. It is a codec-based FP approach with different
  ergonomics and different decode semantics.
- Konform is not "Kotlin's Hibernate Validator." It is a Kotlin DSL, while
  Hibernate Validator is the Bean Validation annotation path.
- `marshmallow` is not "Python's Pydantic." It uses explicit schema objects
  instead of one type-first hybrid definition surface.
- Go's contract generation is externalized. That ergonomic gap is real and
  should be stated directly.
- `dry-schema` and `dry-validation` are a layered pair, not interchangeable
  alternatives.

## Navigation

- `examples/canonical-schema-validation/CATALOG.md` — all examples by language,
  library, and lane
- `examples/canonical-schema-validation/PARITY.md` — cross-language
  consistency rules
- `examples/canonical-schema-validation/domain/models.md` — the shared domain
  specification
- `context/doctrine/schema-validation-contracts.md` — 8 rules governing the arc
- `context/skills/schema-validation-lane-selection.md` — routing decisions by
  lane
- `context/skills/contract-generation-path-selection.md` — schema export and
  drift guidance
- `context/stacks/schema-validation-{language}.yaml` — per-language library
  choices

## Routing Questions This Arc Can Answer

- "Show me Rust contract generation examples" ->
  `rust/serde-schemars/` (Lane B)
- "Show me Python runtime validation" ->
  `python/pydantic/` or `python/marshmallow/` (Lane A)
- "Compare Zod vs Pydantic" ->
  `typescript/zod/` vs `python/pydantic/` (both Lane C)
- "Compare Konform vs Hibernate Validator" ->
  `kotlin/konform/` vs `kotlin/hibernate-validator/`
- "Why is serde + schemars not a validator?" ->
  doctrine Rule 2 and `rust/serde-schemars/README.md`
- "Show interoperability-oriented examples" ->
  Lane B: `rust/serde-schemars/`, `typescript/typebox-ajv/`,
  `elixir/ex-json-schema/`, `go/openapi-generation/`
- "Show teaching-oriented examples" ->
  Lane C: `python/pydantic/`, `typescript/zod/`
- "Detect drift between schema and runtime" ->
  `docs/schema-validation-drift-detection.md`
