# Synthetic Data Realism Doctrine

## The Core Separation

Faker libraries generate realistic atomic values. They do not generate a
realistic relational system by themselves. Do not confuse `faker.name()` with
"generate a correct users table" because table realism depends on ordering,
constraints, cardinality, and validation outside the faker call. Build an
explicit generation pipeline on top of faker instead of stacking more random
value generation and hoping the dataset becomes coherent.

## Seven Mandatory Generation Properties

### Rule 1 — DETERMINISTIC SEED

Every generator must accept an explicit seed and produce identical output for
the same seed on every run on every machine. Document the seed in the example
README and validation report. Test seed reproducibility directly. Never use a
random seed in smoke tests or CI.

### Rule 2 — PARENT-FIRST ORDERING

Generate entities in dependency order: parents before children, roots before
leaves. No child record may reference an ID that has not already been created.
Document the generation order in each example README and keep the code aligned
with that documented order.

### Rule 3 — STABLE ID POOLS

Before generating a dependent layer, build and keep the complete parent ID pool
in memory or in a stable lookup artifact for large profiles. Children must draw
from that stable pool. Do not mint parent IDs on demand while generating
children because partial runs and sampled subsets will break referential
integrity.

### Rule 4 — WEIGHTED DISTRIBUTIONS, NOT UNIFORM RANDOMNESS

Real datasets are skewed. Some organizations are tiny, a few are large, and
activity clusters around a minority of entities. Every canonical example must
demonstrate at least one non-uniform distribution and explain why that
distribution is realistic for the domain.

### Rule 5 — TEMPORAL REALISM

Generated time must respect causality. Parents are created before children,
memberships start after org creation, and events happen during the lifetime of
the entities they reference. Every example must validate that no event
timestamp precedes the creation timestamp of any referenced parent record.

### Rule 6 — CROSS-FIELD CONSISTENCY

Generate related fields together when one field constrains another. If an audit
event carries both `org_id` and `user_id`, that user must belong to that org.
If a project has `created_by`, that user must be a member of the project org.
Do not rely on faker providers to accidentally align constrained fields.

### Rule 7 — VALIDATION BEFORE OUTPUT

Run a validation pass before writing final output. Validation must check
foreign-key integrity, uniqueness for constrained fields, row-count sanity, and
seed reproducibility by comparing two runs with the same seed. The validation
pass must emit a human-readable summary report. Do not commit a canonical
example that writes output without validating it first.

## What Faker Libraries Do Well

- realistic names across locales
- realistic emails, usernames, and URLs
- street addresses, phone numbers, and company names
- lorem text and short product or project labels
- dates within bounded ranges and relative time windows
- UUIDs, IP addresses, and test-only payment identifiers

## What Faker Libraries Do NOT Do

- enforce relational integrity across tables
- model cardinality constraints across an entity graph
- preserve temporal ordering across dependent records
- shape weighted distributions across organizations and events
- coordinate cross-field consistency for constrained relationships
- validate domain-specific business rules before output

## Output Profiles

Every canonical example must implement these profiles or document clearly why a
profile is not applicable.

| Profile | Organizations | Users  | Projects | Events   | Purpose |
|---------|---------------|--------|----------|----------|---------|
| smoke   | 3             | 10     | 9        | ~50      | CI gate, runs in <5s, deterministic |
| small   | 20            | 200    | 100      | ~2,000   | local dev data load |
| medium  | 200           | 5,000  | 2,000    | ~50,000  | realistic demo environment |
| large   | 2,000         | 50,000 | 20,000   | ~500,000 | benchmark or showcase run |

Treat profile counts as additive approximations shaped by the domain's
cardinality rules. Document the actual generated counts in the validation
report instead of pretending the output must match the profile table exactly.

## Commit Rule

Do not commit a faker canonical example until its smoke profile produces a
passing validation report and the language's smoke tests pass.
