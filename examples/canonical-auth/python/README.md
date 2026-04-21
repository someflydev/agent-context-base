# TenantCore IAM Python Canonical Example

## What it is

This is the Python canonical implementation of the TenantCore IAM domain. It demonstrates how to build a multi-tenant, Role-Based Access Control (RBAC) API using FastAPI and PyJWT. This example deliberately uses an in-memory store backed by static JSON fixtures to isolate the teaching focus to authentication, authorization, token claim validation, and route metadata management without the distraction of a real database.

## Requirements

- Python 3.11+
- `uv` (recommended) or `pip`

## How to Run

If you use `uv`:
```bash
uv run uvicorn src.main:app --reload
```

## How to Test

Using `uv`:
```bash
uv run pytest tests/ -v
```

## Key Files and What They Do

- `src/auth/token.py`: Handles token issuance, enforcing the required JWT claim shape (15-min expiry, embedded permissions, `acl_ver`).
- `src/auth/middleware.py`: Defines the FastAPI dependencies (`get_auth_context`, `require_permission`) that extract, validate, and enforce JWT claims against incoming requests.
- `src/registry/routes.py`: Contains `ROUTE_REGISTRY`, a central dictionary mapping paths to required permissions and tenant scopes, which drives both enforcement and `/me` discoverability.
- `src/domain/store.py`: Provides an `InMemoryStore` that loads the canonical test fixtures at startup.
- `src/routes/`: FastAPI routers that implement the canonical flows defined in the domain spec.

## Token Issuance Example

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.example", "password": "password"}'
```

## `/me` Example

```bash
curl -X GET http://127.0.0.1:8000/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Teaching Notes

This example is a simplification for educational purposes:
- **In-Memory Store:** In a real-world production application, the `InMemoryStore` would be replaced by a robust relational database (like PostgreSQL) with proper indexing, caching, and connection pooling.
- **Refresh Tokens:** This example focuses purely on short-lived access tokens. A real system would implement a secure mechanism for refresh tokens or session rotation.
- **HS256 Test Mode:** The codebase uses RSA keys (`RS256`) by default, but allows an override via `TENANTCORE_TEST_SECRET` to use symmetric `HS256` keys during unit testing for simplicity and speed.
