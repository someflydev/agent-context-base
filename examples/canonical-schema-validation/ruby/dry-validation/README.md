# Ruby - dry-validation (Lane A: Rich Rule Contracts)

## Lane
Lane A: runtime validation using a `Contract` class that wraps a dry-schema.

## The dry-rb Ecosystem Design
`dry-validation` builds on top of `dry-schema`. `dry-schema` handles structure,
presence, type coercion, and basic predicates such as "is this field present"
or "is it an integer." `dry-validation` adds semantic rule blocks for
cross-field and business-level checks once the schema has passed. The
separation is intentional: use `dry-schema` alone when structure is enough,
and add a `Contract` when you need richer rules and domain-specific errors.

## Contract Pattern
Each contract uses a `params` block for the structural schema and `rule`
blocks for semantic checks. Rule blocks run after the schema succeeds, so the
mental model is schema first, business rules second.

## Discriminated Union Limitation
`dry-validation` does not have native discriminated union support. This example
dispatches manually inside the `:data` rule by reading `event_type` and then
checking the expected nested keys.

## Cross-Field Rules
The idiom is `rule(:field1, :field2) { ... }` with access through `values`.
That keeps cross-field logic readable, but still clearly separate from the
schema layer below it.
