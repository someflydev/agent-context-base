# Elixir - Ecto.Changeset (Lane A: Cast-Then-Validate Pipeline)

## Lane
Lane A: runtime validation via a pipeline of cast and validate operations.

## What Ecto.Changeset Is
A changeset is a data structure that carries the original data, the cast
changes, and any accumulated validation errors. It is not a JSON Schema-like
contract artifact; it is the result of running a validation pipeline. You
build it with `cast/3`, chain validation functions, and then inspect
`changeset.valid?` and `changeset.errors`. That pipeline-oriented mental model
is the mainstream Elixir and Phoenix boundary style.

## Cast vs Validate: Two Distinct Phases
`cast/3` converts raw params into typed struct fields, including arrays and
datetimes when they are parseable. The later `validate_*` calls enforce
constraints after that conversion step. A changeset can therefore fail because
the cast could not interpret the input or because the value was typed but still
violated a rule.

## Cross-Field Rules
Cross-field rules live in private helper functions that use `get_field/2` and
`add_error/3`. That is more verbose than a Kotlin DSL, but it keeps the
pipeline readable and the order of operations explicit.

## Discriminated Union Handling
Ecto does not have native discriminated union support. This example casts
`data` as a map and validates its shape manually based on `event_type`.

## Comparison with Norm
`Ecto.Changeset` is pipeline-oriented and close to Phoenix application code.
Norm is more declarative and spec-oriented, which can be better for pure-data
validation outside the Ecto ecosystem.
