# Kotlin: http4k + JJWT + RBAC

## Identity

- Name: `kotlin-http4k-jjwt-rbac`
- Language: Kotlin
- Framework: http4k
- Auth library: `JJWT`
- Aliases: `kotlin-jwt-rbac`, `http4k-auth-api`, `http4k-jjwt`

## Preferred JWT Library

`JJWT` is preferred because it gives Kotlin the same JVM JWT surface used in
the Java example and keeps cross-stack teaching aligned. It handles asymmetric
verification cleanly without forcing a larger security framework. `jose4j` is a
good alternative when broader JOSE features matter, but the canonical pattern
prefers the simpler shared JVM library.

## Core Dependencies

- `http4k-core` — routing and filter chain
- `io.jsonwebtoken:jjwt-*` — parse and validate JWTs
- Kotlin data classes — auth context and `/me` response contracts
- Jackson or Moshi adapter — JSON responses
- http4k testing support — request-level behavior checks

## Auth Architecture

This stack extends `context/stacks/kotlin-http4k-exposed.md` with an auth
filter layered into the normal `http4k` route chain. The filter validates the
token, constructs an auth context, and stores it in `RequestContext`. Handlers
then combine that typed context with route metadata and live tenant state to
enforce RBAC and build `/me`.

## Token Validation Pattern

```kotlin
val claims = Jwts.parser()
    .verifyWith(publicKey)
    .requireIssuer("https://auth.example.test")
    .requireAudience("agent-context-base")
    .build()
    .parseSignedClaims(token)
    .payload
val auth = authContextFactory.fromClaims(claims)
aclVersionService.assertCurrent(auth)
```

## Request Context Pattern

Use `RequestContextLens` or a typed `RequestContextKey` populated by the auth
filter. Do not leak auth state into globals or singletons; pass it through the
request chain.

## Route Metadata Pattern

Maintain a list of `RouteMetadata` data classes adjacent to the route
composition layer. Registry lookups should serve both enforcement helpers and
`/me` route filtering.

## /me Handler Pattern

The `/me` handler reads the typed auth context from the request, hydrates tenant
and group details, filters the route registry, and returns JSON. HTML fragments
are optional and should be derived from the same response model.

## Testing Approach

Use http4k request tests with crafted tokens to verify `401`, `403`, stale
`acl_ver`, and tenant-boundary denial. Include an exact `allowed_routes`
assertion for `/me`.

## Canonical Example Path

`examples/canonical-auth/kotlin/`

## Known Constraints or Tradeoffs

- explicit filters are clear, but registry lookup logic must stay small
- shared JVM library parity with Java is useful, though some Kotlin-first APIs are less terse
- host JVM tooling may be unavailable, so Docker-backed smoke checks remain valuable
