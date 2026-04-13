# Synthetic Data Generator

## When to Use This Archetype

Use this archetype when the primary deliverable is a reproducible synthetic data
generator for development, testing, benchmarking, or demo environments. It is
for structured relational dataset generation, not one-off fixture literals or
inline test-case setup.

## Shape

A generator surface organized around an explicit entity graph, seeded random
pipeline, profile-based scale controls, validation pass, and one or more export
formats such as JSONL, CSV, or SQL seed output. The value of the project is the
generation design itself: deterministic, relational, and explainable.

## Required Context

- `context/doctrine/synthetic-data-realism.md`
- `context/stacks/faker-{language}.yaml`
- `examples/canonical-faker/domain/schema.md`
- `examples/canonical-faker/domain/generation-order.md`

## Common Goals

- parent-first relational generation with stable ID pools
- deterministic seeded replay
- profile-based scale control (`smoke`, `small`, `medium`, `large`)
- JSONL, CSV, or SQL output plus a validation report
- smoke tests that are fast, deterministic, and CI-safe

## Anti-Patterns

- calling faker providers inline without a generation pipeline
- generating children before their parents exist
- using language-native random sources without a fixed seed
- treating faker output as valid without a verification pass
- loading every profile fully in memory when chunked writes are sufficient
- confusing realistic-looking values with relational integrity

## Typical Verification Gate

- smoke profile completes in under 5 seconds
- validation report shows zero FK violations
- two identical-seed runs produce byte-identical JSONL output
- row counts stay within the documented profile tolerance window

## Related Artifacts

- `context/doctrine/synthetic-data-realism.md`
- `context/skills/faker-library-selection.md`
- `context/skills/synthetic-dataset-design.md`
- `context/workflows/add-faker-example.md`
- `manifests/faker-polyglot.yaml`
