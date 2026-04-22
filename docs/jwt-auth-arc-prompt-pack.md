# JWT Auth Arc - Prompt Pack Summary

## Prompt Pack: PROMPT_134-140
This prompt pack adds a complete JWT auth capability area to
`agent-context-base`: auth doctrines, a tenant-aware backend archetype,
language-specific stacks, implementation skills and workflows, a shared
TenantCore IAM domain spec, eight canonical examples, parity tracking, and
hardening docs. The arc is organized as a strict sequence so the shared auth
contract lands before the language examples, and the hardening pass can audit
the finished surface honestly.

**Status:** Complete as of PROMPT_140. All seven prompts have run. This
document is a historical reference explaining how the arc was sequenced and why.

## Files in Order

| Prompt file | Purpose |
| --- | --- |
| `.prompts/PROMPT_134.txt` | Foundation: doctrines, archetype, stacks, skills, workflows, manifest, and router seed entries |
| `.prompts/PROMPT_135.txt` | Shared TenantCore IAM domain spec, fixtures, parity matrix, verification contract, and auth catalog skeleton |
| `.prompts/PROMPT_136.txt` | Python FastAPI + PyJWT and TypeScript Hono + jose implementations |
| `.prompts/PROMPT_137.txt` | Go Echo + golang-jwt/jwt and Rust Axum + jsonwebtoken implementations |
| `.prompts/PROMPT_138.txt` | Java Spring Boot + JJWT and Kotlin http4k + JJWT implementations |
| `.prompts/PROMPT_139.txt` | Ruby Hanami-shaped Rack + ruby-jwt and Elixir Phoenix + Joken implementations |
| `.prompts/PROMPT_140.txt` | Hardening, parity runner, router/catalog polish, architecture map, memory concept, and gap audit |

## Prompt Details

### PROMPT_134
**Delivered:** Five auth doctrines, the `tenant-aware-backend-api` archetype,
eight JWT/RBAC stack files, four auth skills, two workflows, a manifest, and
initial router coverage.

Creates the foundation layer for the arc: five auth doctrines, the
`tenant-aware-backend-api` archetype, eight JWT/RBAC stack files, four auth
skills, two workflows, a manifest, and initial router coverage. The key design
decision was to establish auth policy as doctrine plus routeable repo context
before any implementation code lands. It ran only after the repo’s prompt
sequencing rules and router conventions were already stable.

### PROMPT_135
**Delivered:** The shared TenantCore IAM domain contract — entity model,
permission catalog, JWT claim shape, route metadata specification, `/me`
response shape, deterministic fixtures, parity matrix, and verification
contract.

Created the shared TenantCore IAM domain contract used by every language
implementation. The key design decision was to lock the auth domain before
language implementations, which prevented eight stacks from drifting into eight
slightly different policy systems. PROMPT_134 had to exist first because the
domain spec depended on the arc’s doctrines, archetype, and stack vocabulary.

### PROMPT_136
**Delivered:** Python/FastAPI+PyJWT and TypeScript/Hono+jose implementations,
each with explicit JWT validation, in-memory fixture loading, route registries,
and `/me` discoverability.

Implemented the first two examples: Python and TypeScript. These examples set
the tone for the rest of the arc. The key design decision was to pair a Python
teaching stack with a TypeScript teaching stack early because they are common
operator targets and made the cross-language parity model concrete. PROMPT_135
had to exist first so both examples could conform to the shared contract.

### PROMPT_137
**Delivered:** Go/Echo+golang-jwt and Rust/Axum+jsonwebtoken implementations,
proving the arc works through Go middleware and Rust extractors in strongly
typed ecosystems.

Implemented the Go and Rust examples. The key design decision was to group two
strongly typed systems together because the contrast is about language
ergonomics, not domain semantics. PROMPT_136 had already updated the shared
parity matrix so PROMPT_137 extended, rather than recreated, the status surface.

### PROMPT_138
**Delivered:** Java/Spring Boot+JJWT and Kotlin/http4k+JJWT implementations,
covering JVM auth patterns with full parity — route metadata, permission catalog
enforcement, and `/me`.

Implemented the Java and Kotlin examples. The key design decision was to pair
Java and Kotlin because they share the JVM ecosystem but differ in framework
style and code shape. It depended on PROMPT_135 for the contract and on the
earlier implementation prompts for the established parity update rhythm.

### PROMPT_139
**Delivered:** Ruby/Hanami-shaped Rack+ruby-jwt and Elixir/Phoenix+Joken
implementations, completing the planned language matrix and updating the shared
parity and catalog surfaces.

Implemented the Ruby and Elixir examples. The key design decision was to keep
both implementations explicit and framework-shaped without letting full-stack
conventions obscure token validation, route metadata, or `/me`. All prior
prompts had to exist because PROMPT_139 was the last implementation wave.

### PROMPT_140
**Delivered:** The single-read arc overview document, this prompt-pack summary,
a cross-stack parity runner, router polish, catalog normalization, architecture
map updates, and a durable memory concept.

Hardened and closed out the arc. The key design decision was to reserve
hardening for a separate prompt so the final audit could inspect the entire arc
after all implementation prompts had landed. It ran last because it read the
final parity state and documented any unresolved gaps rather than hiding them.

## How the Arc Was Sequenced

1. `PROMPT_134` created the auth capability foundation.
2. `PROMPT_135` defined the shared TenantCore IAM contract.
3. `PROMPT_136`, `PROMPT_137`, `PROMPT_138`, and `PROMPT_139` ran in order so
   each prompt extended the same parity matrix and catalog without merge churn.
4. `PROMPT_140` ran last, after the prior six prompts existed and baseline
   verification still passed.

## Sequencing Rationale

- Foundation before domain spec keeps doctrines, archetype names, and stack
  vocabulary stable before the shared auth contract references them.
- Domain spec before implementations forces every language to implement the
  same entity model, permission atoms, routes, and `/me` shape.
- Two languages per implementation prompt is a practical review unit: enough
  contrast to prove the pattern is cross-language, but still small enough to
  debug and verify coherently.
- The language groupings follow ecosystem affinity: Python + TypeScript as
  common backend teaching stacks, Go + Rust as explicit typed backend stacks,
  Java + Kotlin as JVM stacks, Ruby + Elixir as framework-shaped dynamic
  backend stacks.
- A separate hardening prompt is necessary because overview docs, parity
  tooling, router polish, and architecture-map truthfulness depend on the final
  post-implementation state.

## How This Arc Fits agent-context-base
Before this arc, the repo had capability areas for analytics, schema
validation, and synthetic data, but no canonical auth surface that showed JWT,
RBAC, tenant isolation, and `/me` as one system. The arc fits the repo’s
existing shape cleanly: doctrines under `context/doctrine/`, skills and
workflows under `context/`, a shared domain under `examples/`, parity tooling
under `verification/`, and durable knowledge under `memory/concepts/`. It also
dogfoods the existing TenantCore domain from the faker arc instead of inventing
a parallel auth-only universe.

## Repo Structures Extended

| Structure | Extended by |
| --- | --- |
| `context/doctrine/` | PROMPT_134 |
| `context/archetypes/` | PROMPT_134 |
| `context/stacks/` | PROMPT_134 |
| `context/skills/` | PROMPT_134 |
| `context/workflows/` | PROMPT_134 |
| `manifests/` | PROMPT_134 |
| `context/router/` | PROMPT_134, PROMPT_140 |
| `examples/canonical-auth/domain/` | PROMPT_135 |
| `examples/canonical-auth/{python,typescript}/` | PROMPT_136 |
| `examples/canonical-auth/{go,rust}/` | PROMPT_137 |
| `examples/canonical-auth/{java,kotlin}/` | PROMPT_138 |
| `examples/canonical-auth/{ruby,elixir}/` | PROMPT_139 |
| `verification/auth/` | PROMPT_140 |
| `docs/` | PROMPT_140 |
| `memory/concepts/` | PROMPT_140 |
