# Faker and Synthetic Data Generation Arc

## Purpose
This arc provides a stable way to compare synthetic data generation and faker libraries across ten languages. Cross-language faker comparison requires a shared domain to prevent collapsing distinct ecosystem behaviors into simple atomic data generation. Realistic synthetic data requires an explicit graph layer on top of faker libraries to enforce constraints. After working through these examples, a developer should be able to design a realistic data generation pipeline and choose the right library stack for their language.

**Status:** Complete (PROMPT_119–126). All 10 language examples are implemented and verified. See `examples/canonical-faker/CATALOG.md`.

## The Core Insight
Faker libraries generate realistic atomic values. They do not generate relational systems. The arc explicitly teaches building the graph layer on top: parent-first ordering, ID pools, weighted distributions, temporal realism, and cross-field consistency. Every example demonstrates this pattern.

## The Seven Mandatory Generation Properties
The full specifications are in `context/doctrine/synthetic-data-realism.md`. The rules are:
- Rule 1 — Deterministic Seed
- Rule 2 — Parent-First Ordering
- Rule 3 — Stable ID Pools
- Rule 4 — Weighted Distributions, Not Uniform Randomness
- Rule 5 — Temporal Realism
- Rule 6 — Cross-Field Consistency
- Rule 7 — Validation Before Output

## The TenantCore Domain
TenantCore is a fictional SaaS multi-tenant platform used exclusively for generating canonical synthetic datasets. It forces every language example to handle realistic relational and cardinality challenges.
The domain includes 7 entities:
- **organizations**: The root of the domain.
- **users**: Globally unique identities.
- **memberships**: Associates users with organizations.
- **projects**: Organization-scoped resources.
- **audit_events**: Activity log tying users, projects, and organizations together.
- **api_keys**: Organization credentials tied to specific users.
- **invitations**: Pending or accepted requests to join an organization.
The examples support 4 output profiles:

- **smoke** (seed=42, 3 orgs / 10 users / ~50 audit events — deterministic, for CI gates)
- **small** (20 orgs / 200 users / ~2,000 audit events — fast local runs)
- **medium** (200 orgs / 5,000 users / ~50,000 audit events — realistic volume, demo/staging)
- **large** (2,000 orgs / 50,000 users / ~500,000 audit events — performance and batch testing)

See `examples/canonical-faker/domain/profiles.md` for full per-entity row count targets.

## Language Matrix

| Language     | Primary Library       | Secondary              | Key Teaching Surface            |
|--------------|-----------------------|------------------------|---------------------------------|
| Python       | Faker + Mimesis       | factory_boy            | Multi-locale, schema-based gen  |
| JavaScript   | @faker-js/faker       | Chance                 | Distribution helpers, seeding   |
| Go           | gofakeit              | go-faker/faker         | Struct-tag vs. imperative       |
| Rust         | fake (fake-rs)        | none                   | Builder pattern, typed pipeline |
| Java         | Datafaker             | none                   | Orchestration above providers   |
| Kotlin       | kotlin-faker          | Datafaker              | DSL vs. JVM interop             |
| Scala        | Datafaker (JVM)       | none                   | Functional pipeline, LazyList   |
| Ruby         | faker                 | ffaker                 | faker vs. ffaker contrast       |
| PHP          | FakerPHP/Faker        | Nelmio Alice           | Imperative vs. declarative      |
| Elixir       | Faker                 | ExMachina              | Functional Enum pipeline, Mix   |

_none = no mainstream secondary library recommended for this language; the primary library is sufficient for the full TenantCore domain._

## Verification Status
- All ten language examples are implemented and verified. See
  `examples/canonical-faker/CATALOG.md` for per-language status.
- Repo-wide context validation still passes:
  `python3 scripts/validate_context.py` and
  `python3 scripts/run_verification.py --tier fast`.
- Parity runner: `verification/faker/run_parity_check.py`

## Key Distinctions to Preserve

- Faker libraries generate realistic atomic values. They do NOT provide relational integrity. Every example builds the graph layer explicitly.
- PHP's Alice is a different paradigm from imperative FakerPHP — use it to show declarative fixture definition, not as a replacement for a full pipeline.
- Scala's faker ecosystem is thin — this is documented honestly; Datafaker via JVM interop is the recommended path.
- Elixir's `:rand.seed/2` seeds the process-level RNG, which affects both `:rand` calls and the Faker library's internal randomness.
- Mimesis's schema-based generation (Schema + Field) is a different idiom from Faker's imperative provider calls — both produce the same domain.
- factory_boy (Python) is for small-volume object graph fixtures, not for production-scale dataset generation.
- ExMachina (Elixir) has the same scope as factory_boy — small volume, test use.
- The smoke profile (seed=42) must be deterministic across all runs and machines.

## Navigation

- `examples/canonical-faker/CATALOG.md`        — all examples by language, status
- `examples/canonical-faker/domain/schema.md`  — entity graph spec
- `examples/canonical-faker/domain/generation-order.md` — 7-stage generation sequence
- `examples/canonical-faker/domain/profiles.md` — row count targets
- `context/doctrine/synthetic-data-realism.md` — 7 generation rules
- `context/skills/faker-library-selection.md`  — library selection guide
- `context/skills/synthetic-dataset-design.md` — 7-step pipeline design
- `context/stacks/faker-{language}.yaml`       — per-language library choices

## Routing Questions This Arc Can Answer

- "Show me Python realistic data generation" → python/ (faker or mimesis pipeline)
- "Show declarative fixture generation in PHP" → php/alice/
- "Show the functional Elixir generation pipeline" → elixir/pipeline.ex
- "Compare gofakeit vs struct-tag-based Go generation" → go/pipeline/
- "Show deterministic seed replay" → any example, smoke profile, seed=42
- "Show how to build FK integrity on top of a faker library" → domain/generation_patterns.py
- "Which faker library for Kotlin?" → context/skills/faker-library-selection.md
- "How do I validate generated output?" → domain/validate_output.py
- "What is the difference between Faker and Mimesis?" → python/mimesis_pipeline/README.md
- "Show large-volume generation" → context/doctrine/synthetic-data-realism.md (Rule 7), then the relevant language's medium/large profile implementation
