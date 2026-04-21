# Canonical Auth Example - Java

## What it is
This is the Java (Spring Boot + JJWT) canonical implementation for the TenantCore IAM domain. It demonstrates issuing and validating JWTs, parsing identity context into Spring's `SecurityContext`, enforcing permissions with `@PreAuthorize`, and surfacing `/me` context.

## Requirements
- Java 21+
- Maven 3.9+

## How to run
```bash
mvn spring-boot:run
```

## How to test
```bash
mvn test
```

## Key files and what they do
- `JwtFilter.java`: Custom `OncePerRequestFilter` to validate Bearer tokens and populate the `SecurityContext`.
- `JwtService.java`: Issues standard-shape JWTs using JJWT, and parses them securely.
- `SecurityConfig.java`: Spring Security configuration, registering the filter and disabling CSRF/state.
- `RouteRegistry.java`: The shared route metadata registry used by both RBAC and `/me`.
- `InMemoryStore.java`: Loads the common `users.json`, `tenants.json`, etc.

## Token issuance example
```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.example","password":"password"}'
```

## /me example
```bash
curl http://localhost:8080/me -H "Authorization: Bearer <TOKEN>"
```

## Teaching notes
- **Spring Security minimal setup**: This example eschews the heavy Spring OAuth2 server in favor of a simpler custom filter. This maps better to the canonical auth architecture and allows direct control of the JWT claim shape.
- **@PreAuthorize**: Used to enforce RBAC via `hasAuthority(...)` populated from the custom JWT `permissions` claim.
- **JJWT v0.12**: Uses the modern fluent API (e.g. `Jwts.builder()` and `Jwts.parser().verifyWith()`).
