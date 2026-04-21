# Canonical Auth Example: Go (Echo + golang-jwt/jwt)

This is the canonical Go implementation of the JWT Auth arc, demonstrating tenant-aware RBAC using `echo` and `golang-jwt/jwt`.

## Requirements
- Go 1.22 or later

## How to run
```bash
go run ./main.go
```
The server will start on port 8080.

## How to test
```bash
go test ./...
```

## Dependencies
- `github.com/labstack/echo/v4`: Router and middleware chain
- `github.com/golang-jwt/jwt/v5`: Token parsing and claim validation

## Token Issuance Example
```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.example","password":"password123"}'
```

## /me Example
```bash
curl http://localhost:8080/me \
  -H "Authorization: Bearer <your_token>"
```

## Teaching Notes
- Uses explicit middleware for JWT parsing.
- Uses `c.Set("auth", &authCtx)` to store typed authorization context in the request lifecycle.
- Reads `acl_ver` from the token and invalidates if stale against the database.
- Implements `/me` response dynamically filtering the allowed routes.