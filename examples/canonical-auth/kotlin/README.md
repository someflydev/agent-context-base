# Canonical Auth Example - Kotlin

## What it is
This is the Kotlin (`http4k` + `JJWT`) canonical implementation for the
TenantCore IAM domain. It demonstrates explicit filter-chain JWT validation,
request-scoped auth context, route-metadata-driven discoverability, and
permission enforcement for tenant-aware APIs.

## Requirements
- Kotlin 1.9+
- Java 21+
- Gradle 8+

## How to run
```bash
gradle run
```

## How to test
```bash
gradle test
```

## Key files and what they do
- `src/main/kotlin/dev/tenantcore/auth/Main.kt` builds the `http4k` route tree.
- `auth/JwtMiddleware.kt` validates Bearer tokens and hydrates request auth context.
- `auth/TokenService.kt` issues and parses canonical JJWT tokens.
- `domain/InMemoryStore.kt` loads shared fixtures and computes effective permissions.
- `registry/RouteRegistry.kt` is the shared policy map for enforcement and `/me`.
- `routes/MeRoutes.kt` builds the canonical `/me` response.

## Token issuance example
```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.example","password":"password"}'
```

## /me example
```bash
curl http://localhost:8080/me \
  -H "Authorization: Bearer <TOKEN>"
```

## Teaching notes
- `http4k` keeps the route surface explicit, so permission filters stay visible.
- `RequestContextKey` carries validated auth state without globals.
- `JJWT` v0.12 keeps the JVM token builder and parser flow aligned with Java.
- `allowed_routes` and `guide_sections` come from the same route registry used
  by the filters, so docs and policy do not diverge.
