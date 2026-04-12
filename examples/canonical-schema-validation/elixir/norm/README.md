# Elixir - Norm (Lane A: Declarative Spec-Oriented Validation)

## Lane
Lane A: declarative specs conforming data. Inspired by Clojure's spec.

## What Norm Is
Norm uses `schema/1` and `spec/1` to describe data shapes and predicates.
`conform/2` returns `{:ok, data}` or `{:error, errors}`, while `conform!/2`
raises on mismatch. The mental model is "does this value conform to the spec"
rather than "apply validation steps to a changeset."

## Comparison with Ecto.Changeset
`Ecto.Changeset` is a cast-then-validate pipeline with explicit intermediate
state. Norm is stateless spec conformance against data that is already in the
expected shape. Ecto is the mainstream Phoenix boundary choice, while Norm is
better suited to library code, pure-data validation, or cases where bringing
in Ecto would be excessive.

## Cross-Field Rules
Norm can express cross-field rules with custom predicates over the whole map.
That makes them possible, but less ergonomic than named private helper
functions in an Ecto pipeline.
