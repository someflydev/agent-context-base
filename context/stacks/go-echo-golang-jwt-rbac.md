# Go: Echo + golang-jwt/jwt + RBAC

## Identity

- Name: `go-echo-golang-jwt-rbac`
- Language: Go
- Framework: Echo
- Auth library: `golang-jwt/jwt`
- Aliases: `go-jwt-rbac`, `echo-auth-api`, `echo-golang-jwt`

## Preferred JWT Library

`golang-jwt/jwt` is preferred because it is focused, idiomatic, and widely used
for straightforward JWT validation in Go services. It keeps the mental model
small for claim parsing and verification. `lestrrat-go/jwx` is a strong
alternative when the service needs heavier JOSE features, but that broader scope
is unnecessary for the canonical auth examples.

## Core Dependencies

- `github.com/labstack/echo/v4` — router and middleware chain
- `github.com/golang-jwt/jwt/v5` — token parsing and claim validation
- Go standard `crypto/rsa` or `crypto/ecdsa` — verification keys
- typed Go structs — auth context, route metadata, and `/me` response
- `net/http/httptest` — request-level verification

## Auth Architecture

This stack extends `context/stacks/go-echo.md` with explicit auth middleware.
An Echo middleware parses the bearer token, validates the claims, loads the
current `acl_ver`, and stores the resulting auth context with `c.Set()`.
Handlers then retrieve typed auth state, resolve route metadata, and apply
tenant and permission checks before calling domain services.

## Token Validation Pattern

```go
func RequireAuth(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        token := readBearer(c.Request().Header.Get("Authorization"))
        claims := &AccessClaims{}
        parsed, err := jwt.ParseWithClaims(token, claims, keyFunc,
            jwt.WithAudience("agent-context-base"),
            jwt.WithIssuer("https://auth.example.test"),
        )
        if err != nil || !parsed.Valid {
            return echo.NewHTTPError(http.StatusUnauthorized)
        }
        auth := buildAuthContext(*claims)
        if err := assertACLVersion(c.Request().Context(), auth); err != nil {
            return echo.NewHTTPError(http.StatusUnauthorized)
        }
        c.Set("auth", auth)
        return next(c)
    }
}
```

## Request Context Pattern

Use middleware plus `c.Set("auth", auth)` and a typed accessor helper to keep
auth request-scoped. Avoid package-level globals for “current user” state.

## Route Metadata Pattern

Define a `[]RouteMetadata` registry and keep it adjacent to route registration.
Each entry should include method, path, permission, and tenant scope. Handler
helpers and `/me` filtering read from the same slice.

## /me Handler Pattern

The `/me` handler reads the auth context from Echo, loads live tenant and group
details, filters the metadata registry to accessible routes, and returns a typed
JSON payload. HTML is optional and should come from the same data source.

## Testing Approach

Use `httptest` to send real HTTP requests with crafted tokens through the Echo
router. Cover invalid signature or audience, missing permission, wrong tenant,
and a successful `/me` response whose `allowed_routes` set is exact.

## Canonical Example Path

`examples/canonical-auth/go/`

## Known Constraints or Tradeoffs

- method and path matching must stay explicit because Echo route names are not enough
- Go keeps auth wiring visible, but that means more manual helper code
- `RS256` key handling is slightly more verbose than `HS256`, intentionally
