# Faker and Synthetic Data Generation Arc

## Durable Facts

- The core insight: faker libraries generate realistic atomic values; they do NOT provide relational integrity. Every example builds the graph layer explicitly on top of faker.
- Parent-first generation and stable ID pools are mandatory (Rules 2–3). Violating this order creates FK violations that cannot be fixed without regenerating the entire dataset.
- Every example uses seed 42 for its smoke profile. This must not change.
- Alice (PHP), ExMachina (Elixir), and factory_boy (Python) are factory-style tools for small-volume test fixtures. They are NOT replacements for a production-scale generation pipeline.
- Scala's native faker ecosystem is thin. Datafaker (JVM) is the recommended path for Scala.
- Elixir's `:rand.seed/2` seeds the process-level RNG. This affects both `:rand` calls and the Faker library's internals. Seed once at startup.
- The language-agnostic validator (`validate_output.py`) can validate output from ANY language implementation. Use it in all smoke tests.

## Key Files

| Artifact        | Path                                              | Purpose                    |
|-----------------|---------------------------------------------------|----------------------------|
| Doctrine        | `context/doctrine/synthetic-data-realism.md`      | 7 generation rules         |
| Archetype       | `context/archetypes/synthetic-data-generator.md`  | project shape              |
| Skills          | `context/skills/synthetic-dataset-design.md`      | 7-step pipeline guide      |
| Overview        | `docs/faker-arc-overview.md`                      | human-readable summary     |
| Domain          | `examples/canonical-faker/domain/schema.md`       | TenantCore spec            |
| Reference impl  | `examples/canonical-faker/domain/generation_patterns.py` | Python reference       |
| Validator       | `examples/canonical-faker/domain/validate_output.py` | FK + cross-field check    |
| Catalog         | `examples/canonical-faker/CATALOG.md`             | all 10 examples            |