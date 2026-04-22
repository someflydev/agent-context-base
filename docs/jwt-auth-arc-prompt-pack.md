# JWT Auth Arc - Prompt Pack Summary

## Prompt Pack: PROMPT_134-140
This prompt pack adds a complete JWT auth capability area to
`agent-context-base`: auth doctrines, a tenant-aware backend archetype,
language-specific stacks, implementation skills and workflows, a shared
TenantCore IAM domain spec, eight canonical examples, parity tracking, and
hardening docs. The arc is organized as a strict sequence so the shared auth
contract lands before the language examples, and the hardening pass can audit
the finished surface honestly.

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
Creates the foundation layer for the arc: five auth doctrines, the
`tenant-aware-backend-api` archetype, eight JWT/RBAC stack files, four auth
skills, two workflows, a manifest, and initial router coverage. The key design
decision is to establish auth policy as doctrine plus routeable repo context
before any implementation code lands. It should run only after the repo’s
prompt sequencing rules and router conventions are already stable.

### PROMPT_135
Creates the shared TenantCore IAM domain contract used by every language
implementation. It defines the entity model, permission catalog, JWT claim
shape, route metadata specification, `/me` response shape, deterministic
fixtures, parity matrix, and verification contract. The key design decision is
to lock the auth domain before language implementations, which prevents eight
stacks from drifting into eight slightly different policy systems. PROMPT_134
must exist first because the domain spec depends on the arc’s doctrines,
archetype, and stack vocabulary.

### PROMPT_136
Implements the first two examples: Python and TypeScript. These examples set
the tone for the rest of the arc by showing explicit JWT validation, in-memory
fixture loading, route registries, and `/me` discoverability in two common web
ecosystems. The key design decision is to pair a Python teaching stack with a
TypeScript teaching stack early because they are common operator targets and
make the cross-language parity model concrete. PROMPT_135 must already exist so
both examples can conform to the shared contract.

### PROMPT_137
Implements the Go and Rust examples. These examples prove the arc is not tied
to dynamic languages or decorator-heavy frameworks by showing the same TenantCore
IAM contract through Go middleware and Rust extractors. The key design
decision is to group two strongly typed systems together because the contrast
is about language ergonomics, not domain semantics. PROMPT_136 should already
have updated the shared parity matrix so PROMPT_137 can extend, not recreate,
the status surface.

### PROMPT_138
Implements the Java and Kotlin examples. This prompt covers JVM-auth patterns
while preserving parity with the earlier stacks, including route metadata,
permission catalog enforcement, and `/me`. The key design decision is to pair
Java and Kotlin because they share the JVM ecosystem but differ in framework
style and code shape. It depends on PROMPT_135 for the contract and on the
earlier implementation prompts for the established parity update rhythm.

### PROMPT_139
Implements the Ruby and Elixir examples. These complete the planned language
matrix with a Hanami-shaped Rack service and a Phoenix + Plug service. The key
design decision is to keep both implementations explicit and framework-shaped
without letting full-stack conventions obscure token validation, route
metadata, or `/me`. All prior prompts must already exist because PROMPT_139 is
the last implementation wave and updates the same shared parity and catalog
surfaces.

### PROMPT_140
Hardens and closes out the arc. It adds the single-read overview document, the
human-readable prompt-pack summary, a cross-stack parity runner, router polish,
catalog normalization, architecture map updates, and a durable memory concept.
The key design decision is to reserve hardening for a separate prompt so the
final audit can inspect the entire arc after all implementation prompts have
landed. It must run last because it reads the final parity state and documents
any unresolved gaps rather than hiding them.

## Execution Order

1. Run `PROMPT_134` to create the auth capability foundation.
2. Run `PROMPT_135` to define the shared TenantCore IAM contract.
3. Run `PROMPT_136`, `PROMPT_137`, `PROMPT_138`, and `PROMPT_139` in order so
   each prompt extends the same parity matrix and catalog without merge churn.
4. Run `PROMPT_140` only after the prior six prompts exist and baseline
   verification still passes.

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
