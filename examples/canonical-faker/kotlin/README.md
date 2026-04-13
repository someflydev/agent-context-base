# Canonical Faker Kotlin Example

This example keeps two JVM paths side by side:

- `KotlinFakerPipeline.kt` for the Kotlin-first pipeline surface
- `DatafakerPipeline.kt` for Java-library interop notes and shared-provider teams

## What It Demonstrates

- Kotlin data classes with snake_case JSON annotations
- `buildList`/collection-first graph construction and deterministic `Random(seed)`
- the kotlin-faker vs Datafaker tradeoff, documented honestly
- validation before output

## Seeding Note

The primary pipeline keeps seed flow explicit with `kotlin.random.Random(seed)`.
That makes the smoke profile replayable even if teams later swap in deeper
kotlin-faker provider calls. The secondary Datafaker file shows JVM interop.

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
