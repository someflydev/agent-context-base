# Canonical Faker: Scala

This example demonstrates generating the synthetic TenantCore dataset using Datafaker on the JVM via Scala interop. It illustrates a functional pipeline approach on top of an object-oriented generator.

## ECOSYSTEM NOTE
**Scala-native faker libraries are limited or unmaintained as of 2024.** This example uses Datafaker (Java) via JVM interop. The Scala value comes from the functional pipeline layer: LazyList generation, case classes, immutable Maps for pools, and idiomatic Scala patterns above Datafaker's provider API.

## Seeding
Deterministic generation is achieved by passing a seeded `java.util.Random` instance to Datafaker (`new Faker(new java.util.Random(seed))`).

## Pipeline Architecture
The pipeline uses `LazyList` for lazy evaluation and streaming generation without requiring a heavyweight streaming library.
For medium/large profiles, consider upgrading to ZIO Stream or fs2 when backpressure and async chunked writes matter.

## Quick Start
```bash
sbt "run --profile smoke"
```

## Testing
```bash
sbt test
```
