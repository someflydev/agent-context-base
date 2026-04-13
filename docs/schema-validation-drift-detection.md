# Schema Drift Detection Guide

## What Is Drift?

Drift happens when runtime validation behavior and the exported JSON Schema or
OpenAPI contract stop describing the same payload rules. A service may still
reject bad input correctly at runtime while publishing a stale schema that says
the input is valid. Drift also happens in the other direction: a schema can
become stricter or structurally different from the actual wire format. This is
an interoperability problem, not just a local validation problem.

## When Drift Matters

- When a JSON Schema or OpenAPI spec is published for external consumers
- When cross-language teams share a contract and one side changes independently
- When the schema is committed to version control as a baseline artifact
- When the contract is used to generate client code in another language

## Detection Strategies

### 1. Round-Trip Fixture Check

This is the simplest strategy and applies in every language.

Procedure:

1. Serialize a known-valid domain object to JSON.
2. Validate that JSON against the exported schema.
3. Assert that the schema accepts it.
4. Load a known-invalid object from `fixtures/invalid/`.
5. Validate it against the exported schema.
6. Assert that the schema rejects it.

This catches gross drift such as missing required fields, wrong field types, or
incorrect required/optional behavior. It does not catch every cross-field rule,
because the runtime validator can enforce constraints that JSON Schema cannot
fully express.

### 2. Committed Schema Baseline + Regeneration Diff

Use this in CI when the schema is a published artifact.

Procedure:

1. Commit the exported schema to version control.
2. Regenerate the schema in CI from the current model source.
3. Diff the fresh artifact against the committed baseline.
4. Fail CI if the files differ.

This catches field additions, removals, type changes, renamed serialized fields,
and `serde` or annotation changes that alter wire shape. In this arc, the Rust
`serde-schemars` example and the Go OpenAPI-generation example both model this
baseline strategy.

### 3. Parity Matrix Runner

When multiple implementations share one domain and one fixture corpus, a parity
runner catches behavioral drift between implementations. This repo provides
`verification/schema-validation/run_parity_check.py` for the Python examples so
the universally required fixture rules in `PARITY.md` can be checked from one
entry point. Other languages keep their parity checks in toolchain-specific
test runners.

## Per-Language Notes

### Python (Pydantic)

`model_json_schema()` derives from the same `BaseModel` definition used for
runtime validation, so local drift risk is low. The real risk appears when the
exported schema is committed, copied, or published separately from the model
source. If the schema is an external contract, commit the baseline and diff it
in CI anyway.

### TypeScript (TypeBox)

TypeBox schemas are JSON Schema natively, so drift inside one codebase is low.
The main risk is version skew in the validator or hand-edited schema output.
If Ajv is part of the contract path, pin its version and keep one fixture-based
accept/reject check in CI.

### Go

Go has the highest drift risk in this arc because the runtime validation path
and contract generation path are usually separate. Struct tags or annotations
can diverge from the schema tooling surface, and comment-driven generators do
not get compiler enforcement. Commit the schema baseline and regenerate it in
CI.

### Rust (serde + schemars)

Drift risk is moderate and usually comes from `serde` representation changes.
If `#[serde(rename = "...")]`, optional-field behavior, or tag configuration
changes, the exported schema changes even if runtime validator logic in
`validator` or `garde` did not. Commit the schema baseline and compare it in CI
after regeneration.

### Elixir (ex_json_schema)

The schema is an external artifact, not the same construct used by
`Ecto.Changeset`. Drift appears when the changeset logic evolves and the JSON
Schema file does not. The primary protection is a round-trip fixture check with
at least one known-valid and one known-invalid payload.

## The Cross-Field Rule Gap

JSON Schema can express some conditional rules, especially with `if` / `then` /
`else`, but it cannot capture every domain invariant cleanly. A rule such as
"if plan is free, max sync runs must stay under 10" may be representable, while
other semantic rules remain easier or only possible in runtime code. That means
an exported contract can intentionally be weaker than runtime enforcement. When
that happens, document the gap explicitly and, if the schema is published, use
`$comment` or surrounding docs to state which stricter rules remain runtime-only.
