# TenantCore IAM Ruby Canonical Example

## What it is

This is the Ruby canonical implementation of the TenantCore IAM domain. It
shows a Rack service with Hanami-like boundaries using `ruby-jwt` for JWT issuance and
verification, an in-memory fixture-backed store, a machine-readable route
registry, and a `/me` discoverability endpoint driven by effective
permissions.

## Requirements

- Ruby 2.6+
- Bundler

## How to run

```bash
bundle exec rackup
```

## How to test

```bash
bundle exec rspec
```

Fallback when you need direct Ruby invocation:

```bash
bundle exec ruby -Ilib -Ispec spec/**/*_spec.rb
```

## Token issuance example

```bash
curl -X POST http://127.0.0.1:9292/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.example","password":"password"}'
```

## `/me` example

```bash
curl http://127.0.0.1:9292/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Teaching notes

- `ruby-jwt` is used directly, not through Devise or Warden, so claim
  validation stays explicit.
- The request-scoped auth context is stored in Rack env and read by the route
  handlers, which keeps the code Hanami-shaped without taking a hard runtime
  dependency on Hanami itself.
- The example uses an in-memory fixture store so the teaching focus stays on
  token validation, RBAC, `acl_ver`, and tenant isolation.
- `RS256` is the default documented shape, but `TENANTCORE_TEST_SECRET`
  switches tests to `HS256` for simpler local execution.
- In a Rails or Hanami codebase, framework-integrated auth libraries may be a
  better fit; this example stays lower-level on purpose so the JWT and RBAC
  invariants are explicit.
