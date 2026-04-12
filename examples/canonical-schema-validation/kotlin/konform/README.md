# Kotlin - Konform (Lane A: Kotlin-First DSL Validation)

## Lane
Lane A: rules defined in a Kotlin DSL, not in annotations. Data classes stay clean.

## The Konform DSL
`Validation<T> { }` is the entry point for Konform. Inside the block, you
reference properties such as `WorkspaceConfig::name { ... }` and compose field
rules with constraint helpers like `minLength`, `maxLength`, `pattern`,
`minimum`, `maximum`, and `maxItems`. The result is a `ValidationResult<T>`:
either `Valid` or `Invalid` with structured errors. For cross-field rules,
Konform's idiomatic move is `addConstraint { config -> ... }`, which keeps the
logic in Kotlin code instead of pushing it into annotations or reflection.

## Comparison with Hibernate Validator
Konform keeps rules in code, which makes validators composable, explicit, and
Kotlin-idiomatic. It does not depend on reflection or a framework container,
so it fits pure Kotlin libraries and service code that want validation without
annotation clutter. Hibernate Validator puts rules directly on the data class
fields through Jakarta Bean Validation annotations, which is familiar to Java
and Spring teams and integrates naturally with `@Validated` controller flows.
Choose Konform when the project wants clean models plus explicit validation
objects. Choose Hibernate Validator when framework integration is the priority.

## Cross-Field Rules
This example uses `addConstraint` for plan-tier limits and critical review
rules. Konform does not provide a special multi-field watch primitive; a
predicate over the full object is the idiomatic way to express those checks.
