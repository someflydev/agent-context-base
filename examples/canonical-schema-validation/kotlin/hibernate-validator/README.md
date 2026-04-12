# Kotlin - Hibernate Validator (Lane A: JVM Annotation-Based)

## Lane
Lane A: annotation-driven struct validation. The Jakarta Bean Validation standard.

## When to Use This Approach
Use this style in framework-integrated JVM applications, especially Spring
Boot, Quarkus, and Jakarta EE services. It is also a strong fit for teams with
heavy Java background who want controller-level `@Validated` flows and shared
Bean Validation conventions.

## Cross-Field Rules Require Custom Annotations
Konform can express a plan-tier rule with a short `addConstraint` lambda. In
Hibernate Validator, the same rule usually needs a custom class annotation, a
`ConstraintValidator` implementation, and the annotation applied to the model.
That is more verbose, but it is the standard JVM way to keep cross-field logic
inside the Bean Validation lifecycle.

## Comparison with Konform
The key tradeoff is placement. Hibernate Validator co-locates rules on the
data class through annotations, which makes framework consumption easy but also
mixes validation metadata into the model definition. Konform keeps models free
of validation annotations and defines explicit validator objects instead.
