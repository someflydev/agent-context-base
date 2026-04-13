# Seed Registry

## Purpose

Every canonical faker example must use a fixed seed for its smoke profile. This
file documents the canonical seeds used across the arc.

## Canonical Seeds

| Profile | Seed | Notes |
| --- | --- | --- |
| smoke | 42 | Used in all smoke tests. Must not change. |
| small | 1000 | Stable reference small dataset. |
| medium | 5000 | Stable reference medium dataset. |
| large | 9999 | Benchmark profile; may be overridden for local experiments. |

## Per-Language Seeding

Each language has a different RNG API. The stack files document the seeding
mechanism, but these principles stay fixed:

- The seed must be applied before the first faker or random call.
- The seed must flow through the entire generation pipeline.
- No language-native random call should bypass the seeded generator.
- Two runs with the same seed must produce byte-identical JSONL output.

## Reproducibility Test

Every smoke test must include a reproducibility assertion:

```python
run1 = generate(seed=42, profile="smoke")
run2 = generate(seed=42, profile="smoke")
assert run1 == run2
```
