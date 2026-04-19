# Ruby: Hanami + ruby-jwt + RBAC

## Identity

- Name: `ruby-hanami-ruby-jwt-rbac`
- Language: Ruby
- Framework: Hanami
- Auth library: `ruby-jwt`
- Aliases: `hanami-jwt-rbac`, `ruby-auth-api`, `hanami-ruby-jwt`

## Preferred JWT Library

`ruby-jwt` is preferred because it is the canonical low-level JWT library in
Ruby and keeps the example independent from Rails-specific integration layers.
It is small, well-maintained, and easy to wrap in Hanami middleware or action
helpers. `warden-jwt_auth` is useful in framework-integrated environments, but
it is not the default because the canonical example centers on Hanami, not a
heavier integration stack.

## Core Dependencies

- `hanami` — routing and actions
- `jwt` — token encode/decode and verification
- OpenSSL — RSA or ECDSA key support
- typed Ruby structs or hashes — auth context and route metadata
- request specs — black-box auth verification

## Auth Architecture

This stack extends `context/stacks/ruby-hanami.md` with Rack or Hanami action-
level auth middleware. The middleware validates the token, constructs an auth
context, and stores it in Rack env for the current request. Actions then read
that context, resolve route metadata, and enforce permissions and tenant
boundaries explicitly.

## Token Validation Pattern

```ruby
payload, = JWT.decode(
  token,
  public_key,
  true,
  {
    algorithm: "RS256",
    iss: "https://auth.example.test",
    verify_iss: true,
    aud: "agent-context-base",
    verify_aud: true,
    verify_iat: true,
    verify_jti: true,
    verify_not_before: true,
  }
)
auth = build_auth_context(payload)
assert_acl_version!(auth)
```

## Request Context Pattern

Use Rack env or a Hanami action helper to expose a typed auth context per
request. Avoid process-global “current user” helpers because they hide request
boundaries and complicate testing.

## Route Metadata Pattern

Store route metadata in hashes or small value objects keyed by method and path.
The metadata registry should drive both request authorization and `/me`
discoverability.

## /me Handler Pattern

`/me` returns validated identity plus live tenant, group, and route visibility
data. JSON is required. An HTML fragment variant is optional and should reuse
the same filtered route set.

## Testing Approach

Use request specs with crafted tokens covering missing token, wrong audience,
wrong tenant, and insufficient permission. Verify `/me` derives
`allowed_routes` from the shared metadata registry.

## Canonical Example Path

`examples/canonical-auth/ruby/`

## Known Constraints or Tradeoffs

- `ruby-jwt` is low-level by design, so claim validation options must be set explicitly
- Hanami keeps transport logic clean, but Rack env access should stay wrapped
- Docker-backed smoke verification is often simpler than relying on host Ruby setup
