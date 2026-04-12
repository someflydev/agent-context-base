# Go - ozzo-validation (Lane A: Code-Driven Explicit Rules)

## Lane
Lane A: validation rules are in code, not struct tags. Clean struct
definitions.

## Key Patterns Used
`ValidateStruct` with `Field()`, `is.Email`, `Match(regexp)`, explicit
cross-field `if` blocks, and `validation.Errors` maps for accumulated errors.

## Comparison with go-playground/validator
`ozzo-validation` keeps the structs free of validation metadata and puts the
rules directly in code. That makes plan-limit checks, timeline ordering, and
critical-review requirements much easier to read than stringly typed struct
tags. `go-playground/validator` is more compact for simple scalar constraints,
especially when teams like rule proximity to the field definition. Choose ozzo
when validation logic is complex or business-rule heavy; choose
`go-playground/validator` when the problem is mostly field-level constraints.
