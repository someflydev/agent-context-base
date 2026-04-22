# JWT Auth, RBAC, and Multi-Tenant Backend Patterns Arc

## Purpose
This arc teaches JWT-backed authentication as one coherent backend system
instead of a pile of unrelated auth features. The examples tie together token
validation, a platform-owned RBAC catalog, tenant boundary enforcement, route
metadata, and a `/me` endpoint that exposes authorization state clearly. The
same TenantCore IAM domain appears in eight languages so the underlying design
stays visible even when frameworks and libraries change. A developer working
through the arc should come away understanding which invariants belong to the
domain and which parts are merely framework syntax.

## The Core Insight
The database is the source of truth for memberships, groups, permissions, and
tenant relationships. JWT access tokens are short-lived snapshots that speed up
request-time checks, but `acl_ver` is what makes those snapshots revocable when
authorization changes. Route metadata defines the durable permission namespace
at the transport layer, so enforcement and discoverability do not drift apart.
The `/me` endpoint turns that metadata plus live state into a self-documenting
capability surface, which makes the policy model observable instead of hidden.

## The Five Doctrines

| Doctrine | File | Key Rule |
| --- | --- | --- |
| JWT request context | `context/doctrine/jwt-auth-request-context.md` | A JWT is a signed snapshot, not the source of truth; stale tokens must be invalidated with `acl_ver`. |
| RBAC permission taxonomy | `context/doctrine/rbac-permission-taxonomy.md` | Permission atoms follow `{service}:{resource}:{action}` and are platform-owned. |
| Tenant boundary enforcement | `context/doctrine/tenant-boundary-enforcement.md` | `tenant_id` must come from validated auth context, never caller input. |
| Route metadata registry | `context/doctrine/route-metadata-registry.md` | Route metadata is the single source of truth for auth requirements. |
| `/me` discoverability | `context/doctrine/me-endpoint-discoverability.md` | `/me` computes `allowed_routes` from the route registry instead of hardcoding visibility. |

## The Standard Auth Model
The shared entity model includes `users`, `tenants`, `memberships`, `groups`,
`permissions`, `group_permissions`, `user_groups`, and `audit_events`.
Together they model a tenant-aware SaaS IAM system where users join tenants,
groups compose permissions, and audit events make sensitive auth activity
reviewable.

The role hierarchy is `super_admin -> tenant_admin -> tenant_member`, but the
role labels are descriptive shortcuts rather than the final policy namespace.
`super_admin` is global and has no tenant context. `tenant_admin` operates
inside one tenant and composes group access from a platform-owned permission
catalog. `tenant_member` acts only through effective permissions granted by
groups.

The permission taxonomy is `{service}:{resource}:{action}`. Permissions are
portable capability names such as `iam:user:read` and
`billing:subscription:update`, not URL fragments or ad hoc role flags. Route
metadata points at these atoms so docs, enforcement, and `/me` all speak the
same language.

Canonical JWT claims include `iss`, `aud`, `sub`, `exp`, `iat`, `nbf`, `jti`,
`tenant_id`, `tenant_role`, `groups`, `permissions`, and `acl_ver`.
`permissions` and `groups` give a fast request-time snapshot, while `acl_ver`
lets the service reject tokens after group membership or permission-bearing
assignments change. Tokens stay short-lived, but `acl_ver` is the real
revocation lever that keeps short-lived snapshots safe.

## Implementation Matrix

| Language | Framework | JWT Library | Path |
| --- | --- | --- | --- |
| Python | FastAPI | PyJWT | `examples/canonical-auth/python/` |
| TypeScript | Hono (Node 22-compatible) | jose | `examples/canonical-auth/typescript/` |
| Go | Echo | golang-jwt/jwt | `examples/canonical-auth/go/` |
| Rust | Axum | jsonwebtoken | `examples/canonical-auth/rust/` |
| Java | Spring Boot | JJWT | `examples/canonical-auth/java/` |
| Kotlin | http4k | JJWT | `examples/canonical-auth/kotlin/` |
| Ruby | Rack (Hanami-shaped) | ruby-jwt | `examples/canonical-auth/ruby/` |
| Elixir | Phoenix | Joken | `examples/canonical-auth/elixir/` |

## Verification Status
- All eight language rows are now fully marked `[x]` in
  `examples/canonical-auth/domain/parity-matrix.md`.
- TypeScript smoke and unit tests now run on stock Node 22 without requiring
  Bun.
- The Ruby example is verified as a Rack-based implementation with
  Hanami-shaped boundaries and runs under the repo's current Ruby example
  convention without requiring a committed `Gemfile.lock`.

## Audit Notes
- The shared auth domain tests still pass:
  `verification/unit/test_jwt_auth_arc_foundation.py` and
  `verification/unit/test_jwt_auth_arc_domain.py`.
- Repo-wide context validation still passes:
  `python3 scripts/validate_context.py` and
  `python3 scripts/run_verification.py --tier fast`.
- `verification/auth/run_parity_check.py` is green only when the parity matrix
  contains no `[~]` or `[ ]` rows.

## Key Distinctions to Preserve

- The database is the source of truth. The token is a snapshot. Never trust
  token-only data for high-stakes operations without a DB check.
- `acl_ver` is not optional. A token with a stale `acl_ver` must be rejected.
  Missing this check makes group and permission changes ineffective until
  expiry.
- Permissions are named `{service}:{resource}:{action}`. Route URL strings are
  not the permission namespace.
- Route metadata is the source of truth for auth requirements. Inline
  permission checks that bypass the registry create drift.
- Tenant-admin composes from a platform-owned permission catalog. If an example
  allows tenant-admins to invent arbitrary permission atoms, it is wrong.
- `/me` `allowed_routes` must be computed from the route registry filtered by
  effective permissions. A hardcoded list is a defect.
- `super_admin` is a global role with no `tenant_id`. Code that buries
  super-admin logic inside tenant-scoped authorization paths is wrong.
- The canonical examples use in-memory stores. Production systems replace them
  with a real database while preserving the same invariants.
- Python test mode uses `TENANTCORE_TEST_SECRET` for `HS256`, and the other
  languages document a parallel test-only escape hatch. These are teaching
  aids, not production defaults.

## The /me Endpoint Pattern
The `/me` endpoint returns identity fields, active tenant context, groups,
effective permissions, `acl_ver`, and a filtered `allowed_routes` surface. The
key architectural point is that `allowed_routes` is computed from the shared
route registry, not maintained as a second hardcoded policy list. When
`docs_section` metadata is present, `/me` also exposes `guide_sections` so an
HTMX or server-rendered UI can align navigation with backend policy.
See `context/doctrine/me-endpoint-discoverability.md`.

## Navigation

- `examples/canonical-auth/CATALOG.md` — implementation status
- `examples/canonical-auth/domain/spec.md` — entity schema, permission
  catalog, flows, and route metadata
- `examples/canonical-auth/domain/parity-matrix.md` — cross-language status
- `examples/canonical-auth/domain/verification-contract.md` — test
  requirements
- `context/archetypes/tenant-aware-backend-api.md` — archetype overview
- `context/doctrine/jwt-auth-request-context.md` — token validation rules
- `context/doctrine/rbac-permission-taxonomy.md` — permission naming rules
- `context/doctrine/tenant-boundary-enforcement.md` — tenant isolation rules
- `context/doctrine/route-metadata-registry.md` — route annotation rules
- `context/doctrine/me-endpoint-discoverability.md` — `/me` rules
- `context/skills/jwt-middleware-implementation.md` — middleware guidance
- `context/skills/permission-catalog-design.md` — catalog design guidance
- `context/skills/me-endpoint-design.md` — `/me` design guidance
- `context/skills/route-metadata-annotation.md` — route annotation guidance
- `context/workflows/add-protected-endpoint.md` — 8-step workflow
- `context/workflows/add-tenant-aware-canonical-example.md` — 10-step workflow

## Routing Questions This Arc Can Answer

- "How do I add JWT auth to my app?" -> `context/doctrine/jwt-auth-request-context.md`,
  `context/skills/jwt-middleware-implementation.md`
- "What is the permission naming convention?" -> `context/doctrine/rbac-permission-taxonomy.md`
- "Show me RBAC with custom claims in Go." -> `examples/canonical-auth/go/`,
  `context/stacks/go-echo-golang-jwt-rbac.md`
- "Show me RBAC with custom claims in Rust." -> `examples/canonical-auth/rust/`,
  `context/stacks/rust-axum-jsonwebtoken-rbac.md`
- "Show me RBAC with custom claims in Python." -> `examples/canonical-auth/python/`,
  `context/stacks/python-fastapi-pyjwt-rbac.md`
- "How do I build a `/me` endpoint?" -> `context/skills/me-endpoint-design.md`,
  `context/doctrine/me-endpoint-discoverability.md`
- "How do I invalidate stale tokens?" -> `context/doctrine/jwt-auth-request-context.md`
  (Rule 6)
- "How does multi-tenancy work with JWT?" -> `context/doctrine/tenant-boundary-enforcement.md`
- "Show me route metadata in Rust/Axum." -> `examples/canonical-auth/rust/`,
  `context/doctrine/route-metadata-registry.md`
- "What claims should my JWT contain?" -> `examples/canonical-auth/domain/spec.md`
  (`JWT Claim Shape Standard`)
- "How does super-admin work?" -> `examples/canonical-auth/domain/spec.md`
  (`Role Hierarchy`), `context/doctrine/tenant-boundary-enforcement.md`
- "How do I test auth behavior?" -> `examples/canonical-auth/domain/verification-contract.md`,
  any `examples/canonical-auth/<language>/tests/` or `spec/`
- "Show me `/me` in Elixir/Phoenix." -> `examples/canonical-auth/elixir/`,
  `lib/tenantcore_auth/controllers/me_controller.ex`
- "What permissions do I need to read users?" -> `examples/canonical-auth/domain/spec.md`
  (`Route Metadata Specification`)
- "How do I add a new protected endpoint?" -> `context/workflows/add-protected-endpoint.md`
