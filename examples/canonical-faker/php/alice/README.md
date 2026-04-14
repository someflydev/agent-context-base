# Declarative Fixtures with Nelmio Alice

This directory demonstrates how to use Nelmio Alice for generating declarative dataset fixtures.

- Alice uses `@reference` syntax for FK relationships.
- Alice handles simple ranges but NOT weighted distributions natively.
- For weighted distributions, you need custom Faker providers in PHP.
- Alice does NOT enforce `joined_at >= org.created_at` — temporal rules require either a custom provider or post-generation validation.
- Alice is excellent for: readable fixture files, team-readable graph definitions, simple testing scenarios.
- Alice is NOT ideal for: weighted distributions, complex temporal rules, large volumes (>10K rows), programmatic distribution shaping.

This is the honest contrast with imperative generation:
- FakerPHP imperative: full control, handles all 7 doctrine rules.
- Alice declarative: readable, team-friendly, simpler but less flexible.
