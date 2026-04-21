# Canonical Auth Example: Rust (Axum + jsonwebtoken)

This is the Rust implementation of the JWT Auth arc using `axum` and `jsonwebtoken`.

## Requirements
- Rust 1.76+ (stable)

## How to run
```bash
cargo run
```

## How to test
```bash
cargo test
```

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
- Uses Axum extractors to automatically parse and validate the JWT.
- Uses `jsonwebtoken` for parsing and validating.
- The `AuthContext` provides strongly typed authorization state per request.
