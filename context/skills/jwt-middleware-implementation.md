# JWT Middleware Implementation

Use this skill when the task is to add or repair JWT validation middleware in
one of the supported backend stacks.

## When to Use This Skill

- implementing auth middleware for a protected API
- adding JWT validation to an existing route group
- debugging why valid or invalid tokens are handled incorrectly
- standardizing auth error behavior across stacks

## Validation Checklist

- verify signature before trusting claims
- require and validate `exp`
- require and validate `nbf`
- require and validate `iss`
- require and validate `aud`
- require and validate `sub`
- require `iat` and `jti` even when the library does not by default
- validate `tenant_id` on tenant-scoped routes
- compare token `acl_ver` to live auth state when stale-token invalidation matters

## Asymmetric vs Symmetric Key Guidance

Prefer `RS256` or `ES256` when signing and verification should rotate
independently or when multiple services verify the same token. Use `HS256` only
for constrained single-service deployments or test conveniences that are
documented as such. Do not default to symmetric signing because the library API
was shorter.

## Language-Specific Middleware Entry Points

| Language | Entry point |
| --- | --- |
| Python | FastAPI `Depends()` plus `HTTPBearer` helper |
| TypeScript | Hono middleware with `c.set()` |
| Go | Echo middleware group with `c.Set()` |
| Rust | Axum `FromRequestParts` extractor or middleware |
| Java | Spring `Filter` |
| Kotlin | http4k `Filter` chain |
| Ruby | Rack middleware or Hanami before-action helper |
| Elixir | Phoenix Plug |

## Error Response Standard

Return `401` when the token is missing, malformed, expired, wrong-issuer,
wrong-audience, or otherwise invalid. Return `403` when the token is valid but
the effective permissions do not satisfy the route metadata requirement.
Differentiate authentication failure from authorization failure consistently.

## Testing Pattern

Use black-box request tests with crafted tokens instead of unit-testing helper
functions in isolation only. Cover: missing token, expired token, wrong
audience, wrong tenant, valid token without permission, valid token with
permission, and stale `acl_ver`.

## Anti-Patterns

- decoding without signature verification because the route “only reads claims”
- returning `403` for missing or invalid tokens instead of `401`
- relying on framework globals instead of request-scoped auth context
- validating only `exp` and ignoring `iss`, `aud`, `nbf`, or `jti`
