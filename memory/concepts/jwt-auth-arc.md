# Concept: JWT Auth, RBAC, and Multi-Tenant Patterns Arc

## What This Arc Teaches
The auth arc teaches five doctrines as one production-oriented system: token
validation, permission taxonomy, tenant boundary enforcement, route metadata,
and `/me` discoverability. The important lesson is not "how to decode a JWT"
but how to keep authorization structural and observable across different
backend ecosystems. `acl_ver` is the key mechanism that makes short-lived token
snapshots safe, because it lets the service invalidate old authorization state
without pretending every request must do a full policy rebuild. Route metadata
is the single source of truth for route protection, and `/me` is a first-class
capability surface that exposes the result of that policy model clearly.

## The Key Non-Negotiables

- The database is the source of truth. The token is a snapshot.
- `acl_ver` must be checked. Missing this makes permission revocation
  ineffective until token expiry.
- Permission names are `{service}:{resource}:{action}`, not URL paths.
- Tenant-admin composes from the platform permission catalog. No
  tenant-defined permission atoms.
- Route metadata drives enforcement and `/me`. No second policy list.
- `super_admin` has no `tenant_id`. Super-admin logic must not live in the
  normal tenant-scoped permission path.
- `/me` `allowed_routes` is computed from the route registry filtered by
  effective permissions. A hardcoded route list is a defect.

## Library Defaults by Language

| Language | Library | Why |
| --- | --- | --- |
| Python | PyJWT | battle-tested, minimal API |
| TypeScript | jose | ESM-native, runtime-agnostic |
| Go | golang-jwt/jwt | focused, idiomatic |
| Rust | jsonwebtoken | mature crate, good docs |
| Java | JJWT v0.12 | fluent builder, wide adoption |
| Kotlin | JJWT v0.12 | JVM parity with Java example |
| Ruby | ruby-jwt | canonical Ruby JWT base |
| Elixir | Joken | Elixir-native, Plug-friendly |

## The TenantCore IAM Domain
The canonical domain is TenantCore, the same fictional SaaS platform used by
the faker arc. Its entity model includes `users`, `tenants`, `memberships`,
`groups`, `permissions`, `group_permissions`, `user_groups`, and
`audit_events`, which together form a realistic multi-tenant RBAC system. All
eight language examples load the same JSON fixtures from
`examples/canonical-auth/domain/fixtures/`. The fixture data is deterministic
and hardcoded rather than randomly generated so tests stay stable across
languages.

## Test Mode Pattern
All implementations support a test mode built around `TENANTCORE_TEST_SECRET`
and symmetric signing for easier local verification. `RS256` remains the
documented production-like default, while `HS256` is a test-only escape hatch
to avoid full key-management setup in smoke tests and unit tests. Keep the
teaching shortcut explicit; do not silently normalize it into production advice.

## Navigation Shortcuts

- Domain spec: `examples/canonical-auth/domain/spec.md`
- Permission catalog: `spec.md` -> `The Permission Catalog`
- JWT claim shape: `spec.md` -> `JWT Claim Shape Standard`
- All implementations: `examples/canonical-auth/CATALOG.md`
- Cross-stack status: `examples/canonical-auth/domain/parity-matrix.md`
- Primary doctrine: `context/doctrine/jwt-auth-request-context.md`
- Arc overview: `docs/jwt-auth-arc-overview.md`

_Last updated: 2026-04-22_
