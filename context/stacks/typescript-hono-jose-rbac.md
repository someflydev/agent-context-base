# TypeScript: Hono + jose + RBAC

## Identity

- Name: `typescript-hono-jose-rbac`
- Language: TypeScript
- Framework: Hono
- Auth library: `jose`
- Aliases: `hono-jwt-rbac`, `bun-auth-api`, `typescript-jose`

## Preferred JWT Library

`jose` is preferred because it is modern, ESM-native, and works well in Bun or
Node.js while covering the JOSE surface cleanly. It makes asymmetric signing and
verification straightforward without locking the example to legacy Node-only
APIs. `jsonwebtoken` remains a valid alternative for older Node.js services,
but it is not the default because the canonical stack favors Bun-compatible,
spec-oriented tooling.

## Core Dependencies

- `hono` — router and request context
- `jose` — JWT verify/sign functions and key utilities
- `zod` or typed interfaces — auth context and `/me` response shaping
- `bun:test` or equivalent runner — black-box auth tests
- optional `tsx` or Bun runtime helpers — local execution ergonomics

## Auth Architecture

A Hono middleware validates the bearer token with `jose`, constructs an auth
context, and stores it on `c.set("auth", ...)`. Route handlers read that state,
load the route metadata entry for the current request, and enforce permission
and tenant boundaries from one registry. `ES256` is the default signing mode
because it pairs well with Bun and `jose`, but the pattern remains compatible
with `RS256`.

## Token Validation Pattern

```ts
const authMiddleware = createMiddleware(async (c, next) => {
  const token = readBearerToken(c.req.header("Authorization"));
  const { payload } = await jwtVerify(token, publicKey, {
    issuer: "https://auth.example.test",
    audience: "agent-context-base",
  });
  const auth = await buildAuthContext(payload);
  await assertAclVersion(auth);
  c.set("auth", auth);
  await next();
});
```

## Request Context Pattern

Store the validated auth context on `c.set()` and read it through a small typed
helper so handlers do not parse ad hoc payloads. Keep the state request-scoped
inside Hono’s context rather than in module-level caches.

## Route Metadata Pattern

Define route metadata objects next to Hono route registration and keep them in a
shared registry keyed by method and path pattern. Middleware and `/me` filtering
should both consume that registry instead of hand-maintained permission arrays.

## /me Handler Pattern

`/me` returns token-derived identity plus live tenant, group, and route
visibility details. JSON is required. HTML fragments are optional but should use
the same registry-filtered `allowed_routes` payload if present.

## Testing Approach

Craft tokens with valid and invalid `iss`, `aud`, expiry, and `tenant_id`
claims, then send requests through the real Hono app. Assert `401` for missing
or invalid credentials, `403` for permission failures, and exact route
visibility on `/me`.

## Canonical Example Path

`examples/canonical-auth/typescript/`

## Known Constraints or Tradeoffs

- `jose` is precise and explicit, but the key APIs are more verbose than older libraries
- Bun and Node.js both work, but Bun should stay the teaching baseline
- path-pattern matching for registry lookups must be implemented carefully
