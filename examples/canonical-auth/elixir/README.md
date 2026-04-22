# TenantCore IAM Elixir Canonical Example

## What it is

This is the Elixir canonical implementation of the TenantCore IAM domain. It
uses Phoenix controllers plus a Plug pipeline, `Joken` for JWT handling, a
GenServer-backed in-memory fixture store, and a shared route registry that
powers both RBAC enforcement and `/me` discoverability.

## Requirements

- Elixir 1.16+
- Erlang/OTP 26+
- Mix

## How to run

```bash
mix phx.server
```

## How to test

```bash
mix test
```

## Token issuance example

```bash
curl -X POST http://127.0.0.1:4000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.example","password":"password"}'
```

## `/me` example

```bash
curl http://127.0.0.1:4000/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Teaching notes

- `Joken` keeps claim validation explicit and Plug-friendly without dropping to
  lower-level JOSE APIs for every call site.
- The in-memory store is a GenServer because Phoenix examples commonly route
  domain state through supervised processes, even when the backing data is only
  a fixture corpus.
- The authenticated pipeline stores validated auth context in
  `conn.assigns.auth`, which keeps request scope visible and testable.
- The `/me` response is built from token claims plus live store and route
  registry data, not from a raw decode echo.
- This is intentionally a Phoenix controller example, not a LiveView example,
  because the auth arc is teaching request pipelines and API discoverability.
- `RS256` is the documented default shape; `TENANTCORE_TEST_SECRET` enables
  `HS256` in tests to avoid key management overhead.
