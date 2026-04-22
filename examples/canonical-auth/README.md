# Canonical Auth Examples

JWT-backed authentication, RBAC, and tenant-aware backend patterns implemented
across eight backend language ecosystems.

## Implementations

| Language | Path | Notes |
| --- | --- | --- |
| Python | `python/` | FastAPI + PyJWT |
| TypeScript | `typescript/` | Hono + jose |
| Go | `go/` | Echo + golang-jwt |
| Rust | `rust/` | Axum + jsonwebtoken |
| Java | `java/` | Spring Boot + JJWT |
| Kotlin | `kotlin/` | http4k + JJWT |
| Ruby | `ruby/` | Hanami + ruby-jwt |
| Elixir | `elixir/` | Phoenix + Joken |

## Navigation

- `CATALOG.md` — per-language status, verification level, and known gaps
- `domain/spec.md` — shared JWT, permission, and route contract
- `docs/jwt-auth-arc-overview.md` — arc goals, design decisions, and scope
- `docs/jwt-auth-arc-gaps.md` — documented parity gaps and environment blockers

## Shared Domain

All implementations use the same fixture data, permission catalog, and route
contract from `domain/`. The shared contract ensures cross-language parity is
testable and that an example can be compared directly against any other.

## Verification

```bash
# Run the cross-language parity check
python3 verification/auth/run_parity_check.py

# Run the fast repo verification suite
python3 scripts/run_verification.py --tier fast
```

Known parity gaps are documented in `docs/jwt-auth-arc-gaps.md` rather than
hidden by skipping or stubbing.
