# Workflow: Add a Faker Example

## When to Use This Workflow

Use this workflow when adding a new canonical synthetic-data example under
`examples/canonical-faker/`. It is for relational dataset generation examples,
not for ad hoc inline fixtures inside application tests.

## Steps

1. Read `context/doctrine/synthetic-data-realism.md` and confirm the seven rules.
2. Read `examples/canonical-faker/domain/schema.md` to understand the entity graph.
3. Read `examples/canonical-faker/domain/generation-order.md` to confirm the parent-first order.
4. Read `context/stacks/faker-{language}.yaml` for the target language.
5. Read `examples/canonical-faker/CATALOG.md` to see what already exists.
6. Create the example directory under `examples/canonical-faker/{language}/`.
7. Implement the generation pipeline using `context/skills/synthetic-dataset-design.md`.
8. Implement at least the `smoke` and `small` output profiles.
9. Add smoke tests under `verification/faker/{language}/`.
10. Run the smoke profile and confirm the validation report passes.
11. Update `examples/canonical-faker/CATALOG.md` to register the new example.
12. Run `python3 scripts/validate_context.py`.
13. Commit with a `[PROMPT_XXX]` subject prefix.

## Scope Boundaries

DO:
- implement atomic generation, relational graph rules, validation, and JSONL or CSV output
- document the seed, generation order, and distribution choices
- keep smoke tests deterministic and CI-safe

AVOID:
- adding new domain entities without updating `domain/schema.md`
- committing before smoke tests and validation pass
- using language-native random sources outside the seeded generator
- hiding graph rules inside opaque fixture helpers with no ordering documentation
