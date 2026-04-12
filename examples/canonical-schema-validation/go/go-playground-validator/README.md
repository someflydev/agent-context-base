# Go - go-playground/validator (Lane A: Tag-Based Struct Validation)

## Lane
Lane A: struct tags drive validation. Reflect-based at runtime.

## Key Tag Patterns Used
`validate:"required,email"`, `validate:"oneof=free pro enterprise"`, `dive`
for slice items, custom `RegisterValidation()` hooks for the slug and
signature formats, and `omitempty` for nullable fields.

## Limitations of Tag-Based Validation
Tags keep simple field rules close to the struct definition, but they stop
being ergonomic once the rules depend on multiple fields at once. Cross-field
checks such as `finished_at >= started_at` and the free/pro plan limits for
`max_sync_runs` are handled in `validate/validate.go`, not in the struct tags.
Conditional requirements such as `due_at` for critical review requests also
need explicit code. Discriminated union dispatch for `WebhookPayload.data`
cannot be expressed as a tag either, so the validator package only handles the
field-level pieces. The result is compact for scalar constraints and awkward
for business logic.

## Comparison with ozzo-validation
`ozzo-validation` moves rules out of struct tags and into explicit validation
functions. That makes cross-field logic easier to read and test, especially for
timeline and conditional requirements. `go-playground/validator` is terser for
simple structs, but the tag strings get harder to reason about as soon as the
domain includes business rules.

## Contract Generation
Go has no inline schema derivation surface equivalent to Pydantic or
`schemars`. See `../openapi-generation/` for the Go contract lane example
(Lane B).
