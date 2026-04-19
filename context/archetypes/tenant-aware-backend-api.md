# Tenant-Aware Backend API (JWT Auth + RBAC)

## Identity

- Name: `tenant-aware-backend-api`
- Domain: Authentication, authorization, and multi-tenant SaaS backends
- Aliases: `jwt-protected-api`, `rbac-api`, `multi-tenant-api`

## When To Use This Archetype

Use this archetype when:

- the service must protect endpoints with JWT-based auth
- multiple tenants share the same service but must remain isolated
- RBAC drives route protection and UI visibility
- a `/me` discoverability endpoint is part of the contract
- route metadata must power docs, enforcement, and guide generation

Do not use this archetype when:

- auth is handled entirely by a gateway and the service never inspects tokens
- the service is fully public and has no protected endpoints
- the system is single-user or single-tenant and has no RBAC need

## Shape

This archetype describes a single backend service with explicit JWT validation,
tenant-aware request context, route metadata, and a platform-owned permission
catalog. The service may expose JSON APIs only, or JSON plus HTMX-friendly HTML
fragments. The important constraint is that auth policy stays structural and
machine-readable instead of dissolving into handler-specific conditionals.

## Core Capabilities

- JWT validation middleware for signature, expiry, issuer, audience, and claims
- request-scoped auth context carrying user, tenant, groups, and permissions
- route metadata registry with permission, scope, and docs annotations
- RBAC enforcement driven by metadata instead of inline string checks
- super-admin path for explicit cross-tenant operations
- tenant-admin path for group and membership management inside one tenant
- tenant-user path constrained by effective permissions
- `/me` endpoint with JSON output and optional HTMX HTML variant
- platform-owned permission catalog used to compose group permissions
- authorization version tracking with `acl_ver` for stale-token invalidation
- audit trail for sensitive auth and cross-tenant operations
- smoke tests covering token issuance, validation, RBAC denial, and `/me`

## Directory Shape

```text
<language>/
  README.md
  src/ or app/
    auth/         # JWT middleware, token builder, claims, validation rules
    routes/       # protected endpoints and framework router registration
    domain/       # users, tenants, groups, permissions, memberships
    registry/     # route metadata registry and permission catalog
    me/           # /me handler and response shaping
    tests/        # unit and smoke tests
  fixtures/       # shared fixture JSON loaded at startup
```

## Doctrines Activated

- `context/doctrine/jwt-auth-request-context.md`
- `context/doctrine/rbac-permission-taxonomy.md`
- `context/doctrine/tenant-boundary-enforcement.md`
- `context/doctrine/route-metadata-registry.md`
- `context/doctrine/me-endpoint-discoverability.md`
- `context/doctrine/testing-philosophy.md`

## Canonical Examples

| Language | Path | Status |
| --- | --- | --- |
| Python | `examples/canonical-auth/python/` | planned |
| TypeScript | `examples/canonical-auth/typescript/` | planned |
| Go | `examples/canonical-auth/go/` | planned |
| Rust | `examples/canonical-auth/rust/` | planned |
| Java | `examples/canonical-auth/java/` | planned |
| Kotlin | `examples/canonical-auth/kotlin/` | planned |
| Ruby | `examples/canonical-auth/ruby/` | planned |
| Elixir | `examples/canonical-auth/elixir/` | planned |

## Stacks

- `context/stacks/python-fastapi-pyjwt-rbac.md`
- `context/stacks/typescript-hono-jose-rbac.md`
- `context/stacks/go-echo-golang-jwt-rbac.md`
- `context/stacks/rust-axum-jsonwebtoken-rbac.md`
- `context/stacks/java-spring-jjwt-rbac.md`
- `context/stacks/kotlin-http4k-jjwt-rbac.md`
- `context/stacks/ruby-hanami-ruby-jwt-rbac.md`
- `context/stacks/elixir-phoenix-joken-rbac.md`

## Routing Questions This Archetype Answers

- "How should a JWT-protected multi-tenant API be structured?"
- "Where does tenant isolation actually get enforced?"
- "How should route permissions be modeled so docs and enforcement stay aligned?"
- "What should `/me` return in a teachable RBAC system?"
- "How do I distinguish tenant-admin from super-admin cleanly?"
- "Where should `acl_ver` be checked and incremented?"
- "Which stack file matches JWT auth in my target language?"
- "How do I avoid raw path strings as permission names?"
- "How do I keep HTMX navigation aligned with backend permissions?"
- "What does the canonical directory layout look like for auth examples?"
