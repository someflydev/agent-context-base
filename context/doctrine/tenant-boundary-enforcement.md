# Tenant Boundary Enforcement

## Core Principle

Every tenant-scoped resource belongs to exactly one tenant. The authenticated
token’s `tenant_id` claim defines the active tenant context for the request.
No endpoint may read or write another tenant’s resources based on caller input
or transport shortcuts. Tenant isolation must be structural in middleware,
handlers, and storage access.

## Rules

Rule 1 — `tenant_id` must be validated at every request boundary.
Auth middleware or extractors must verify the tenant claim before protected work
begins. Skipping tenant checks on “internal” routes is how cross-tenant leaks
happen. If a route is tenant-scoped, the tenant boundary is enforced on every
request.

Rule 2 — Tenant context flows via validated auth context, not caller input.
`tenant_id` comes from the validated token or an explicit super-admin path. It
does not come from a body field, query parameter, or untrusted header. Caller-
supplied tenant context is an impersonation vector, not a convenience.

Rule 3 — Super-admin calls are explicitly distinguished.
Cross-tenant super-admin behavior must live on a separate code path or an
explicitly flagged registry entry. Tenant-user and tenant-admin handlers should
not contain hidden “unless super-admin” branches. Structural separation keeps
tenant rules honest and auditable.

Rule 4 — Tenant isolation in data access must be structural.
Queries for tenant-scoped data must include `WHERE tenant_id = ?` or the
equivalent filter derived from validated auth context. That clause must not be
assembled from request body fields. ORM abstractions are acceptable only when
they preserve visible tenant scoping guarantees.

Rule 5 — Membership must be verified, not assumed.
A valid token for tenant `X` is not proof that the user is still an active
member of tenant `X`. Sensitive operations should verify live membership and
authorization version. Tokens can carry membership snapshots for speed, but the
system must be able to invalidate them quickly.

Rule 6 — Audit every cross-tenant boundary touch.
Super-admin operations that inspect or mutate tenant-scoped state across tenant
boundaries must emit audit events. Log the acting principal, target tenant,
action, timestamp, and outcome. Cross-tenant power without auditability is a
governance bug.

## Anti-Patterns

- accepting `tenant_id` from the request body or query string on protected routes
- deriving tenant scope from URL shape instead of validated auth context
- burying super-admin bypasses inside normal tenant-scoped handlers
- issuing unscoped tenant queries and filtering the result set later
- trusting old membership snapshots without `acl_ver` or live verification
