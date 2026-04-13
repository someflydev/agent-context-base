# Canonical Faker Examples - Catalog

## Domain

All examples generate the TenantCore domain described in `domain/schema.md`.

## Examples By Language

| Language | Primary Library | Secondary/Graph Library | Status | Path |
| --- | --- | --- | --- | --- |
| Python | Faker + Mimesis | factory_boy | [x] PROMPT_121 | python/ |
| JavaScript | `@faker-js/faker` | Chance | [ ] PROMPT_122 | javascript/ |
| Go | gofakeit | go-faker/faker | [ ] PROMPT_122 | go/ |
| Rust | fake (fake-rs) | - | [ ] PROMPT_123 | rust/ |
| Java | Datafaker | - | [ ] PROMPT_123 | java/ |
| Kotlin | kotlin-faker | Datafaker | [ ] PROMPT_123 | kotlin/ |
| Ruby | faker | ffaker | [ ] PROMPT_124 | ruby/ |
| PHP | FakerPHP/Faker | Nelmio Alice | [ ] PROMPT_124 | php/ |
| Scala | Datafaker (JVM) | - | [ ] PROMPT_125 | scala/ |
| Elixir | Faker | ExMachina | [ ] PROMPT_125 | elixir/ |

## Domain Artifacts

- `domain/schema.md` - entity graph, field definitions, and constraints
- `domain/generation-order.md` - canonical 6-stage generation sequence
- `domain/seed-registry.md` - canonical seeds by profile
- `domain/profiles.md` - row count targets by profile
- `domain/generation_patterns.py` - Python reference implementation

## Validation

- `domain/validate_output.py` - language-agnostic JSONL validator
- `verification/faker/` - per-language smoke and structural test suites
