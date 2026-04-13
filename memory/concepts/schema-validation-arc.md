# Concept: Schema Validation and Contract Generation Arc

## Durable Facts

- The three-lane model is the organizing principle for this capability area:
  Lane A is runtime validation, Lane B is contract generation, and Lane C is
  hybrid type-driven modeling. Do not collapse them into one generic category.
- Rust's `serde + schemars` path belongs to Lane B. `serde` defines serialized
  shape, `schemars` exports the contract, and runtime validation belongs to
  `validator` or `garde`.
- `io-ts` is not a simpler Zod. It is a codec-based FP design where decode
  returns an `Either`, and its ergonomics and teaching value differ from Zod.
- Konform and Hibernate Validator represent different Kotlin philosophies.
  Konform is a DSL-first Kotlin path; Hibernate Validator is the annotation and
  framework-integration path.
- `marshmallow` and Pydantic represent different Python philosophies.
  Pydantic is a type-first hybrid surface; `marshmallow` uses explicit schema
  objects.
- `dry-schema` and `dry-validation` are layered, not interchangeable.
  `dry-schema` covers structural validation and schema shape; `dry-validation`
  adds richer semantic rules.
- Go does not have one dominant library that unifies type definition, runtime
  validation, and schema export. The contract lane is externalized; that is an
  ecosystem reality, not a repo omission.

## Key Files

| Artifact | Path | Purpose |
| --- | --- | --- |
| Doctrine | `context/doctrine/schema-validation-contracts.md` | 8 rules, 3-lane model |
| Archetype | `context/archetypes/polyglot-validation-lab.md` | Project shape |
| Skills | `context/skills/schema-validation-lane-selection.md` | Routing by lane |
| Overview | `docs/schema-validation-arc-overview.md` | Single-read arc summary |
| Domain | `examples/canonical-schema-validation/domain/models.md` | 5-model shared spec |
| Catalog | `examples/canonical-schema-validation/CATALOG.md` | All 18 examples |

_Last updated: 2026-04-12_
