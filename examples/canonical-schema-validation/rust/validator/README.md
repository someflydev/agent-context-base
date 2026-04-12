# Rust - validator (Lane A: Derive-Based Struct Validation)

## Lane
Lane A: `#[derive(Validate)]` on structs. Field-level rules via attributes.

## The Three-Library Separation
Rust keeps deserialization, runtime validation, and contract export in
different libraries on purpose. `serde` controls the wire shape: field names,
enum representations, optional fields, and tagged unions. The `validator`
crate runs runtime constraint checks such as string lengths, regex patterns,
and email validation after deserialization succeeds. `schemars` is separate and
reads the Rust type plus `serde` attributes to derive a JSON Schema matching
the serialized representation. That means the validator crate does not know the
serialized field names by itself, and `schemars` does not enforce runtime
acceptance rules. Keeping those responsibilities split makes the contract lane
explicit instead of hiding it behind one magic model type.

## Cross-Field Rules
`validator`'s derive macro cannot express cross-field rules directly. This
example keeps those checks in `validate_cross_fields_sync_run()` and
`validate_workspace_plan()` after the `Validate` derive runs.

## Comparison with garde
`garde` is also derive-based, but it offers a richer rule DSL and better
collection ergonomics. It is stronger when you want more expressive attribute
syntax or contextual validation. `validator` has broader adoption and more
examples across the ecosystem.
