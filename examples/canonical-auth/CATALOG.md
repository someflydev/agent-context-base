# Canonical Auth Examples

JWT auth, RBAC, and tenant-aware backend examples sharing one TenantCore IAM
domain contract.

## Domain

- `domain/spec.md` - authoritative entity, permission, JWT, flow, route, and
  `/me` specification
- `domain/verification-contract.md` - required smoke and unit tests for every
  implementation
- `domain/parity-matrix.md` - cross-language implementation tracking

## Implementations

| Language | Framework | Auth Library | Path | Status |
| --- | --- | --- | --- | --- |
| Python | FastAPI | PyJWT | `examples/canonical-auth/python/` | [x] |
| TypeScript | Hono | jose | `examples/canonical-auth/typescript/` | [x] |
| Go | Echo | golang-jwt/jwt | `examples/canonical-auth/go/` | [x] |
| Rust | Axum | jsonwebtoken | `examples/canonical-auth/rust/` | [x] |
| Java | Spring Boot | JJWT | `examples/canonical-auth/java/` | [ ] |
| Kotlin | http4k | JJWT | `examples/canonical-auth/kotlin/` | [ ] |
| Ruby | Hanami | ruby-jwt | `examples/canonical-auth/ruby/` | [ ] |
| Elixir | Phoenix | Joken | `examples/canonical-auth/elixir/` | [ ] |

## How to Run Any Example

Read the `README.md` in the target example directory for setup, run, and test
commands. Each implementation loads shared fixtures from
`examples/canonical-auth/domain/fixtures/`.

## Parity Status

See `domain/parity-matrix.md` for implementation-level parity and verification
progress across Python, TypeScript, Go, Rust, Java, Kotlin, Ruby, and Elixir.
