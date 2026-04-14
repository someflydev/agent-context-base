# Canonical Faker Kotlin Example

This example keeps two JVM paths side by side:

- `KotlinFakerPipeline.kt` for the Kotlin-first pipeline surface using the
  kotlin-faker DSL and seeded `fakerConfig`
- `DatafakerPipeline.kt` for Java-library interop notes and shared-provider teams

## What It Demonstrates

- Kotlin data classes with snake_case JSON annotations
- kotlin-faker DSL calls such as `faker.company.name()` and `faker.name.name()`
- collection-first graph construction and deterministic `Random(seed)`
- the kotlin-faker vs Datafaker tradeoff, documented honestly
- validation before output

## Seeding Note

The primary pipeline keeps seed flow explicit in two places:

- `fakerConfig { randomSeed = seed }` for kotlin-faker field generation
- `kotlin.random.Random(seed)` for weighted distributions and pool decisions

That split mirrors the same pattern used in the other language examples. The
secondary Datafaker file shows JVM interop when a team already shares Java
faker dependencies.

## Quick Start

```bash
gradle run --args="--profile smoke --output ./output"
```

## Test

```bash
gradle test
```

## Validate Output

```bash
python3 ../domain/validate_output.py --input-dir ./output/smoke
```
