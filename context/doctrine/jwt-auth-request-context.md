# JWT Auth and Request Context

## Core Principle

A JWT access token is a short-lived, signed snapshot of authorization state, not
the source of truth. The database remains authoritative for memberships,
permissions, and tenant relationships. The token exists to accelerate
request-time checks without forcing a full read on every route. Stale tokens
must be detectable with an authorization version claim such as `acl_ver`.

## Rules

Rule 1 — Validate before trusting.
Every protected endpoint must validate signature, expiry, issuer, and audience
before any claim is read. Libraries that make any of those checks optional are
dangerous by default. Canonical examples validate all four on every protected
request.

Rule 2 — Asymmetric signing is preferred.
Use `RS256` or `ES256` when signing and verification should rotate
independently. `HS256` is acceptable only for explicitly constrained
single-service deployments. When `HS256` appears in a canonical example, it is
documented as a teaching shortcut or test convenience, never the default.

Rule 3 — Short-lived access tokens only.
Canonical access tokens expire in 15 minutes or less. Longer TTLs trade away
revocation responsiveness and must be justified inline. Refresh-token flows are
important but outside the scope of the canonical auth examples.

Rule 4 — Standard claims are not optional.
Every token must include `iss`, `aud`, `sub`, `exp`, `iat`, `nbf`, and `jti`.
Missing any of these is a defect, not a simplification. Canonical examples
fail closed when a standard claim is missing or malformed.

Rule 5 — Auth context is request-scoped, not global.
Validated auth state belongs on the request context, extractor, or dependency
graph for the current request. Global mutable auth state is forbidden. In DI
frameworks, the auth context must move through the container or request object,
not a thread-local or process singleton.

Rule 6 — Authorization version enables fast invalidation.
Tokens should carry an `acl_ver` claim matching the user’s current
authorization version. If the token version differs from the stored version,
the token is treated as expired even when `exp` is still in the future.
Increment `acl_ver` whenever group membership, tenant membership, or
permission-bearing assignments change.

Rule 7 — Token claims are a snapshot, not a live query.
Embedded permissions are for fast request-time checks, not for pretending the
database disappeared. Sensitive operations should still perform a live read
when the blast radius is high. Canonical examples document which routes are
token-only versus version-checked against live state.

Rule 8 — Tenant context must be explicit.
Tenant-scoped tokens must carry `tenant_id`, and every tenant-scoped route must
validate that context before work begins. Accepting any valid token without a
tenant check is a cross-tenant access bug. Tenant context may be absent only on
explicit super-admin routes.

## Anti-Patterns

- long-lived access tokens that make `acl_ver` effectively irrelevant
- `HS256` shared secrets in multi-service deployments without a strong reason
- skipping `nbf` or `jti` because the library defaults are easier
- storing current auth state in globals, thread-locals, or process singletons
- using raw URL paths as permission names instead of cataloged permission atoms

## Canonical Library Choices

| Language | Preferred library | Why preferred | Adjacent alternative |
| --- | --- | --- | --- |
| Python | `PyJWT` | Small, battle-tested API with predictable claim validation | `joserfc` for broader JOSE surface |
| TypeScript | `jose` | Modern ESM-native JOSE toolkit for Bun or Node.js | `jsonwebtoken` for legacy Node-only services |
| Go | `golang-jwt/jwt` | Focused, idiomatic, and widely deployed | `lestrrat-go/jwx` for broader JOSE needs |
| Rust | `jsonwebtoken` | Mature crate with clear validation controls | `jwt-simple` for narrower ergonomic flows |
| Java | `JJWT` | Fluent builder, parser, and verification surface | `java-jwt` from Auth0 |
| Kotlin | `JJWT` | JVM parity with Java example and solid docs | `jose4j` for wider JOSE completeness |
| Ruby | `ruby-jwt` | Canonical low-level JWT library for Ruby | `warden-jwt_auth` as framework integration |
| Elixir | `Joken` | Elixir-native configuration and Plug-friendly flow | `JOSE` for lower-level primitives |
