# Ruby - dry-schema (Lane A/B: Schema Foundation + JSON Schema Output)

## Lane
Primarily Lane A for structural validation and coercion. JSON Schema export
adds a limited Lane B capability.

## What dry-schema Does (and Does Not Do)
`dry-schema` handles structure, type coercion, required versus optional keys,
and predicate-based value constraints such as min, max, and inclusion. It does
not handle richer semantic rules like cross-field plan limits, duplicate
reviewer checks, or nuanced custom business messages. For those, the normal
step up is `dry-validation`, which wraps a schema with rule blocks.

## The Layering
The intended stack is `dry-schema -> dry-validation -> application rules`.
Each layer adds power, and each layer is deliberately separate rather than
collapsed into one type-driven model.

## JSON Schema Export
When the JSON Schema extension is available, `dry-schema` can export a schema
description of the structural layer. That output reflects the schema
definition, not the rule blocks you would add in `dry-validation`, so drift
checks should focus on structural parity rather than business-level semantics.
