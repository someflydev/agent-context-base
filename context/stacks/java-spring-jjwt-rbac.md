# Java: Spring Boot + JJWT + RBAC

## Identity

- Name: `java-spring-jjwt-rbac`
- Language: Java
- Framework: Spring Boot 3.x
- Auth library: `JJWT`
- Aliases: `spring-jwt-rbac`, `java-auth-api`, `spring-jjwt`

## Preferred JWT Library

`JJWT` is preferred because it offers a fluent builder and parser surface with
strong documentation and broad adoption in JVM services. It makes asymmetric
signing and standard-claim checks straightforward without pulling in a larger
auth server abstraction. `java-jwt` from Auth0 is a valid alternative, but it
is not the default because `JJWT` maps more directly onto the custom-filter
teaching pattern used here.

## Core Dependencies

- `spring-boot-starter-web` — HTTP transport
- `io.jsonwebtoken:jjwt-*` — JWT parse, sign, and validation support
- `spring-security-core` or minimal filter utilities — request auth context
- Jackson — `/me` response serialization
- Spring test stack — black-box controller and filter tests

## Auth Architecture

Canonical examples use a minimal custom JWT filter, not a full Spring Security
OAuth2 server. The filter validates the token, loads current auth state, and
stores a typed auth context in the request or `SecurityContext`. Controllers or
services then resolve route metadata and enforce permissions from the registry.
This keeps the example teachable while still using Spring’s normal filter flow.

## Token Validation Pattern

```java
Claims claims = Jwts.parser()
    .verifyWith(publicKey)
    .requireIssuer("https://auth.example.test")
    .requireAudience("agent-context-base")
    .build()
    .parseSignedClaims(token)
    .getPayload();
AuthContext auth = authContextFactory.fromClaims(claims);
aclVersionService.assertCurrent(auth);
```

## Request Context Pattern

Store the validated auth context in `SecurityContextHolder` or a request
attribute populated by the filter, then inject it through small helpers. Avoid
thread-local custom globals beyond Spring’s normal request context machinery.

## Route Metadata Pattern

Use a registry bean or explicit annotations that feed one registry. Controllers
should not hardcode permission strings in `if` statements. The registry should
be queryable for `/me` and coverage checks.

## /me Handler Pattern

`/me` combines token identity, live tenant and group state, and filtered route
metadata. JSON is required. HTML is optional and should reuse the same response
model if server-rendered views are added.

## Testing Approach

Run request-level tests through the real filter chain with crafted tokens.
Verify invalid tokens fail with `401`, valid-but-underprivileged tokens fail
with `403`, and `/me` returns route visibility derived from the registry.

## Canonical Example Path

`examples/canonical-auth/java/`

## Known Constraints or Tradeoffs

- Spring can hide control flow if too much auth logic is annotation-driven
- a custom filter is more teachable than a full auth-server setup
- `SecurityContext` should carry typed auth data, not raw claim maps
