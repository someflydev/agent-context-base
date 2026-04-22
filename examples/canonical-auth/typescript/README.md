# TenantCore IAM TypeScript Canonical Example

## What it is

This is the TypeScript canonical implementation of the TenantCore IAM domain. It demonstrates how to build a multi-tenant, Role-Based Access Control (RBAC) API using Hono and `jose`. This example deliberately uses an in-memory store backed by static JSON fixtures to isolate the teaching focus to authentication, authorization, token claim validation, and route metadata management without the distraction of a real database.

## Requirements

- Node.js 22.x or newer
- `npm install`

## How to run

```bash
npm start
```

## How to test

```bash
npm test
```

## Key Files and What They Do

- `src/auth/token.ts`: Handles token issuance, enforcing the required JWT claim shape (15-min expiry, embedded permissions, `acl_ver`).
- `src/auth/middleware.ts`: Defines the Hono middleware (`jwtMiddleware`, `requirePermission`) that extract, validate, and enforce JWT claims against incoming requests.
- `src/registry/routes.ts`: Contains `ROUTE_REGISTRY`, a central array mapping paths to required permissions and tenant scopes, which drives both enforcement and `/me` discoverability.
- `src/domain/store.ts`: Provides an `InMemoryStore` that loads the canonical test fixtures at startup.
- `src/routes/`: Hono routers that implement the canonical flows defined in the domain spec.

## Token Issuance Example

```bash
curl -X POST http://127.0.0.1:3000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.example", "password": "password"}'
```

## `/me` Example

```bash
curl -X GET http://127.0.0.1:3000/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Teaching Notes

This example is a simplification for educational purposes:
- **In-Memory Store:** In a real-world production application, the `InMemoryStore` would be replaced by a robust relational database (like PostgreSQL) with proper indexing, caching, and connection pooling.
- **Refresh Tokens:** This example focuses purely on short-lived access tokens. A real system would implement a secure mechanism for refresh tokens or session rotation.
- **HS256 Test Mode:** The codebase uses `ES256` keys by default, but allows an override via `TENANTCORE_TEST_SECRET` and `TENANTCORE_TEST_ALG` to use symmetric `HS256` keys during unit testing.
- **No Bun Requirement for Verification:** The smoke and unit tests run on stock Node 22, so parity checks do not depend on Bun being installed on the host.
