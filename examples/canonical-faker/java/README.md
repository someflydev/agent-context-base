# Canonical Faker Java Example

This example uses Datafaker as the maintained JVM faker, but the main teaching
surface is the orchestration layer above it.

## What It Demonstrates

- seeded replay with `new Faker(new Random(seed))`
- pure Java 17 record types for the TenantCore entities
- explicit `ArrayList` and `HashMap` pools for parent-first graph generation
- temporal realism with `Instant` arithmetic instead of isolated faker dates

## Quick Start

```bash
mvn compile
mvn exec:java -Dexec.args="--profile smoke --output ./output"
```

## Test

```bash
mvn test
```

## Validate Output

```bash
python3 ../domain/validate_output.py --input-dir ./output/smoke
```

The example is intentionally framework-free: no Spring, no JPA, no Hibernate,
and no database connection. The point is deterministic relational generation.
