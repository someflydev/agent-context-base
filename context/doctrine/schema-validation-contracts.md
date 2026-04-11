# Schema Validation and Contract Generation

## purpose

This doctrine exists to keep runtime validation, schema export, and type-driven
modeling distinct when assistants route tasks across languages. When those
lanes are blurred, assistants recommend the wrong library, misstate what a tool
does, and miss drift risks between runtime behavior and exported contracts.

## the three lanes

### Lane A: Runtime Validation

Lane A checks live values against constraints at execution time. It is about
boundary safety, parsing behavior, error reporting, and whether invalid data is
rejected or coerced. Lane A may support nested rules and cross-field checks,
but it does not inherently produce a machine-readable schema artifact.

### Lane B: Contract Generation and Interoperability

Lane B produces a machine-readable description of the expected structure. The
output is usually JSON Schema, OpenAPI fragments, or a similar contract
artifact consumed by another tool or language. Lane B may derive from runtime
definitions, but its core job is interoperability and drift visibility.

### Lane C: Hybrid Type-Driven Flows

Lane C unifies the model definition, runtime validation, and schema generation
in one construct. The same definition becomes the type, the validator, and the
contract source. This pattern is strongest in Python and TypeScript, while Go
and Elixir usually separate those responsibilities more explicitly.

## rules

### 1. Do not conflate lanes.

A contract-generation library and a validation library can appear in the same
codebase while doing different work. `schemars` and `garde` are not variants of
one tool; one exports contracts and the other enforces runtime rules. Route to
the lane that matches the requested outcome before naming libraries.

### 2. Treat serde + schemars as a contract lane, not just a serialization add-on.

In Rust, `serde` defines the serialized shape and `schemars` derives JSON
Schema aligned with that representation. That pairing is a first-class contract
path for interoperability and drift checks. Do not demote it to incidental
serialization plumbing.

### 3. Explicitly compare Konform and Hibernate Validator in Kotlin contexts.

Kotlin validation is not exhausted by JVM annotations. `Konform` represents a
Kotlin-first DSL with explicit rule composition, while Hibernate Validator
follows the Bean Validation model and framework integration path. A complete
Kotlin comparison names both and states the design tradeoff.

### 4. Distinguish marshmallow from Pydantic in Python contexts.

Pydantic is a hybrid type-driven model where type declarations, validation, and
schema export share one definition surface. `marshmallow` uses explicit schema
objects and a serialization-first design. Both are legitimate choices, but
they sit in different design positions and should not be described as the same
kind of Python validator.

### 5. Preserve io-ts in TypeScript comparisons.

`io-ts` is a codec-based design that couples runtime decoding and encoding with
static type inference. It is not a smaller Zod and it is not interchangeable
with TypeBox. When a task asks for serious TypeScript validation comparisons,
keep `io-ts` in scope unless the operator narrows the comparison explicitly.

### 6. Maintain a shared fixture corpus across language examples.

Canonical schema-validation examples must use the same domain and the same
valid, invalid, and edge fixtures. Without a shared corpus, cross-language
comparison turns into anecdote instead of a contract. Shared fixtures make
parity checks and future drift detection tractable.

### 7. Distinguish drift detection from validation.

Runtime validation answers whether a live payload is accepted or rejected.
Drift detection answers whether the exported contract still matches that real
behavior. A codebase can pass runtime validation tests while its JSON Schema or
OpenAPI output has quietly diverged from the actual acceptance rules.

### 8. Smoke tests must cover at least one valid and one invalid fixture per example.

A valid-only smoke test proves the code runs, not that validation works. Every
canonical example needs at least one accepted fixture and one rejected fixture,
plus explicit edge handling when the library supports coercion or nullable
distinctions.

## what this doctrine does not cover

- input sanitization, xss prevention, or injection defense
- authentication and authorization checks at service boundaries
- database constraints, migrations, and storage-layer invariants
- orm-level validation and persistence callbacks
- exhaustive library api documentation or cookbook usage
