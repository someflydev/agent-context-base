# Python Canonical Faker Example

This example is the Python reference implementation for the TenantCore faker
arc. It demonstrates three library surfaces that produce the same domain-shaped
JSONL output:

- `Faker`: multi-locale, custom-provider, imperative value generation
- `Mimesis`: schema-oriented and batched atomic generation
- `factory_boy`: declarative object-graph factories for smoke and small runs

Library matrix:

| Pipeline | Primary strength | Best fit |
| --- | --- | --- |
| Faker | locale breadth, familiar API | canonical reference and readable generation code |
| Mimesis | schema-driven batching | larger flat-value generation with explicit graph code |
| factory_boy | declarative factories | smoke fixtures and small object-graph examples |

Quick start:

```bash
pip install -r requirements.txt
python3 generate.py --pipeline faker --profile smoke --output-dir ./output
```

Profiles and typical runtime:

- `smoke`: CI-safe, deterministic seed `42`, usually under a second
- `small`: local development dataset, a few seconds
- `medium`: realistic demo volume, noticeably slower and more memory-heavy
- `large`: benchmark scale; defined here but better exercised outside CI

Relational integrity is handled explicitly in graph code, not by the faker
libraries themselves. The shared domain layer enforces parent-first ordering,
stable ID pools, temporal realism, and cross-field constraints before any
output is written.

Reference docs:

- `../domain/schema.md`
- `../domain/generation-order.md`
