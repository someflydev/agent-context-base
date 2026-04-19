# Rust: Axum + jsonwebtoken + RBAC

## Identity

- Name: `rust-axum-jsonwebtoken-rbac`
- Language: Rust
- Framework: Axum
- Auth library: `jsonwebtoken`
- Aliases: `rust-jwt-rbac`, `axum-auth-api`, `axum-jsonwebtoken`

## Preferred JWT Library

`jsonwebtoken` is preferred because it is the most mature JWT crate in the Rust
ecosystem for this problem shape and gives direct control over validation
configuration. It pairs well with Axum extractors and typed claim structs.
`jwt-simple` is a viable alternative for narrower, more ergonomic flows, but it
is not the default because the canonical examples value explicit validation
knobs.

## Core Dependencies

- `axum` — routing, extractors, and response handling
- `jsonwebtoken` — decode, validate, and sign tokens
- `serde` — claim and response serialization
- `tower` or Axum middleware utilities — request pipeline wiring
- `tokio` test stack — request-level behavior verification

## Auth Architecture

This stack extends `context/stacks/rust-axum-modern.md` with an auth extractor
or `FromRequestParts` implementation that validates the bearer token and builds
an `AuthContext`. The extractor performs issuer, audience, expiry, and standard
claim checks up front, then applies `acl_ver` invalidation before the handler
runs. Route metadata lives in a static registry and is reused by both auth
checks and `/me` response generation.

## Token Validation Pattern

```rust
let validation = Validation {
    validate_exp: true,
    validate_nbf: true,
    aud: Some(HashSet::from(["agent-context-base".to_string()])),
    iss: Some(HashSet::from(["https://auth.example.test".to_string()])),
    algorithms: vec![Algorithm::RS256],
    required_spec_claims: HashSet::from([
        "iss".into(), "aud".into(), "sub".into(), "exp".into(),
        "iat".into(), "nbf".into(), "jti".into(),
    ]),
    ..Validation::default()
};
let data = decode::<AccessClaims>(token, &decoding_key, &validation)?;
```

## Request Context Pattern

Prefer an Axum extractor or `Extension<AuthContext>` built per request.
Handlers should receive typed auth state as an argument, not through globals or
ambient mutable state.

## Route Metadata Pattern

Use a static slice of `RouteMetadata` structs describing method, path,
permission, tenant scope, and docs section. A small registry lookup helper can
resolve the current request and power both RBAC enforcement and `/me`.

## /me Handler Pattern

The `/me` handler returns typed JSON built from the validated auth extractor,
live membership data, and the filtered route registry. If HTML is added later,
it should render from the same domain object rather than from a second auth
projection.

## Testing Approach

Exercise the real Axum router with crafted tokens using async request tests.
Cover `401` for invalid signature or stale `acl_ver`, `403` for missing
permissions, and tenant mismatch rejection.

## Canonical Example Path

`examples/canonical-auth/rust/`

## Known Constraints or Tradeoffs

- registry lookup needs explicit route-pattern handling because runtime paths are concrete
- Axum extractors keep handlers clean, but the error typing can be verbose
- asymmetric key parsing should stay in small helpers to avoid noisy handlers
