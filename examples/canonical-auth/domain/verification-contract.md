# Verification Contract - Canonical Auth Examples

## Scope
This contract defines the minimum automated proof required before a canonical
auth implementation is marked complete in the parity matrix and catalog. It
covers JWT issuance and validation, RBAC enforcement, tenant-boundary denials,
`/me` discoverability, and route-registry coverage. It does not prescribe a
database engine, exact HTML layout, or framework-specific wiring beyond the
shared domain spec.

## Required Smoke Tests

1. `token_issue_success`
   Description: valid credentials produce a signed JWT with the canonical claim
   shape.
   Actor: any seeded user.
   Input: email + password or canonical test credential payload.
   Expected outcome: `200` with token fields present; fail fast on missing
   standard claims.

2. `token_invalid_credentials`
   Description: invalid credentials are rejected.
   Actor: anonymous caller.
   Input: correct email + wrong password.
   Expected outcome: `401`; fail fast if a token is issued anyway.

3. `token_expired_rejection`
   Description: expired tokens are denied before any route work begins.
   Actor: any user with an expired token.
   Input: Bearer token with `exp` in the past.
   Expected outcome: `401`; fail fast if the handler body executes.

4. `token_stale_acl_ver`
   Description: stale authorization versions are rejected.
   Actor: any tenant-scoped user.
   Input: valid token whose `acl_ver` trails the stored user row.
   Expected outcome: `401`; fail fast if protected routes still authorize.

5. `get_me_success`
   Description: `/me` returns the canonical response shape.
   Actor: any valid token holder.
   Input: Bearer token.
   Expected outcome: `200` with identity, tenant context, permissions,
   `allowed_routes`, and timestamps.

6. `get_me_unauthorized`
   Description: `/me` rejects anonymous access.
   Actor: anonymous caller.
   Input: no Bearer token.
   Expected outcome: `401`; fail fast on partial or downgraded data.

7. `rbac_permission_granted`
   Description: a caller with the required permission can access a protected
   route.
   Actor: seeded user with the matching permission.
   Input: valid token plus request to a protected route.
   Expected outcome: `200`; fail fast on unexpected `403`.

8. `rbac_permission_denied`
   Description: a caller without the required permission is rejected.
   Actor: seeded user lacking the permission.
   Input: valid token plus request to a protected route.
   Expected outcome: `403`; fail fast if access is granted.

9. `cross_tenant_denial`
   Description: tenant A cannot access tenant B resources.
   Actor: tenant member from one tenant.
   Input: valid token plus request targeting another tenant's entity.
   Expected outcome: `403`; fail fast if filtering happens after data fetch.

10. `super_admin_access`
    Description: super admin can call the admin tenant route surface.
    Actor: `super_admin`.
    Input: valid super-admin token.
    Expected outcome: `200` on `/admin/tenants`.

11. `super_admin_tenant_scoped_denial`
    Description: super admin behavior on tenant-scoped routes is explicit.
    Actor: `super_admin`.
    Input: valid super-admin token plus tenant-scoped endpoint request.
    Expected outcome: documented and tested policy, defaulting to `403` when
    tenant context is required.

12. `me_allowed_routes_match_permissions`
    Description: `/me.allowed_routes` must match callable routes.
    Actor: any tenant-scoped user and the super admin.
    Input: valid token and positive plus negative route spot checks.
    Expected outcome: listed routes succeed, omitted routes deny.

## Required Unit Tests

- token builder: canonical claim shape includes all required standard and auth
  claims
- token builder: expiry window is 15 minutes or less from issue time
- permission check: exact permission match returns true
- permission check: missing permission returns false
- route registry: every route declares required metadata fields
- route registry: every referenced permission exists in the catalog
- `/me` response builder: all required fields from the domain spec are present
- `/me` allowed-routes filter: only routes permitted by the effective
  permission set remain

## Parity Commitment
An implementation is complete only when all smoke tests and required unit tests
pass, the shared fixture corpus loads successfully, and that language row is
fully marked `[x]` in `examples/canonical-auth/domain/parity-matrix.md`.
