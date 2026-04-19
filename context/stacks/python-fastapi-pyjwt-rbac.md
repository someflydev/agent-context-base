# Python: FastAPI + PyJWT + RBAC

## Identity

- Name: `python-fastapi-pyjwt-rbac`
- Language: Python
- Framework: FastAPI
- Auth library: `PyJWT`
- Aliases: `fastapi-jwt-rbac`, `fastapi-pyjwt`, `python-auth-api`

## Preferred JWT Library

`PyJWT` is preferred because it is battle-tested, minimal, and widely deployed
in production Python APIs. It keeps claim validation explicit instead of hiding
critical checks behind framework magic. `joserfc` is a capable alternative when
broader JOSE coverage matters, but it is not the default because canonical auth
examples prioritize a smaller teaching surface.

## Core Dependencies

- `fastapi` — HTTP framework and dependency injection surface
- `PyJWT` — token encode/decode and claim validation
- `cryptography` — RSA/ECDSA key handling for `RS256` or `ES256`
- `pydantic` — auth context and `/me` response models
- `httpx` or `pytest` test client equivalent — black-box auth tests

## Auth Architecture

This stack is a companion to `context/stacks/python-fastapi-uv-ruff.md`, not a
replacement. A dependency or `HTTPBearer`-backed auth function validates the
incoming token, loads the current `acl_ver`, and returns a typed auth context.
Handlers receive that context through `Depends()`, then use route metadata to
check permissions and tenant scope. `/me` combines validated token claims with
live registry and membership data before responding.

## Token Validation Pattern

```python
def require_auth(token: str = Depends(bearer_scheme)) -> AuthContext:
    claims = jwt.decode(
        token,
        key=PUBLIC_KEY,
        algorithms=["RS256"],
        audience="agent-context-base",
        issuer="https://auth.example.test",
        options={"require": ["iss", "aud", "sub", "exp", "iat", "nbf", "jti"]},
    )
    auth = build_auth_context(claims)
    assert_acl_version(auth)
    return auth
```

## Request Context Pattern

Use `Depends()` to inject a request-scoped `AuthContext` into protected
handlers. Do not store decoded claims on module globals. When shared helper
logic needs auth state, pass the typed context explicitly.

## Route Metadata Pattern

Maintain a registry list or mapping describing method, path, permission, and
tenant scope. Register that metadata next to the FastAPI router declaration and
use it in both middleware helpers and `/me` route filtering. Decorators are
acceptable only when they feed the same shared registry.

## /me Handler Pattern

The `/me` route reads the validated `AuthContext`, hydrates tenant and group
details from live data, filters the route registry by effective permissions, and
returns typed JSON. If HTML is supported, content negotiation should render a
fragment from the same data model.

## Testing Approach

Use black-box request tests with crafted valid, expired, wrong-audience, and
wrong-tenant tokens. Verify `401` for invalid tokens and `403` for valid tokens
missing the required permission. Include one `/me` assertion that
`allowed_routes` exactly matches the effective permission set.

## Canonical Example Path

`examples/canonical-auth/python/`

## Known Constraints or Tradeoffs

- `HS256` is allowed only as a documented test convenience, not the default
- dependency injection keeps auth explicit but can feel repetitive without small helpers
- live `acl_ver` checks add one read on high-sensitivity routes by design
