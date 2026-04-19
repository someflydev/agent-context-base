# TenantCore IAM Domain Specification

## Purpose
TenantCore IAM is the canonical authentication and authorization domain for the
JWT auth arc. It standardizes the shared entity model, permission catalog, JWT
claim shape, route metadata, fixture corpus, and verification expectations that
all eight language examples must follow. The domain intentionally dogfoods the
same fictional TenantCore SaaS platform used by the faker arc, translating the
existing multi-tenant organization graph into a teachable IAM surface. It is a
good auth teaching domain because it combines short-lived JWTs, tenant
boundaries, global versus tenant-scoped roles, route metadata, and `/me`
discoverability in one small but realistic system.

## Core Entities

### users
Fields: `id` (UUID), `email` (unique), `display_name`, `tenant_id`
(FK -> tenants), `created_at`, `is_active`, `acl_ver` (int, incremented on
permission change)

Notes:
- `email` is globally unique across TenantCore
- `tenant_id` is `null` for the global `super_admin` identity
- `acl_ver` increments when memberships, group assignments, or group permission
  assignments change

### tenants
Fields: `id` (UUID), `slug` (unique), `name`, `created_at`, `is_active`

Notes:
- `tenants` maps the auth arc vocabulary onto the faker arc's TenantCore
  organizations
- all tenant-scoped entities ultimately belong to one tenant

### memberships
Fields: `id` (UUID), `user_id` (FK -> users), `tenant_id` (FK -> tenants),
`tenant_role` (enum: `super_admin` / `tenant_admin` / `tenant_member`),
`created_at`, `is_active`

Notes:
- `super_admin` has no tenant context; `tenant_id` is `null`
- a user has exactly one active membership for the active tenant in this
  canonical example

### groups
Fields: `id` (UUID), `tenant_id` (FK -> tenants), `slug` (unique per tenant),
`name`, `created_at`

Notes:
- group slugs are tenant-local and appear in JWT `groups`
- groups are the only path to permission assignment for tenant users

### permissions
Fields: `id` (UUID), `name` (format: `{service}:{resource}:{action}`),
`description`, `created_at`

Notes:
- this is the platform-owned permission catalog
- tenant admins assign catalog permissions to groups but cannot create new ones

### group_permissions
Fields: `id` (UUID), `group_id` (FK -> groups), `permission_id`
(FK -> permissions), `granted_at`

Notes:
- this join table expresses the permission set for a group
- all rows are tenant-safe because `group_id` already determines tenant scope

### user_groups
Fields: `id` (UUID), `user_id` (FK -> users), `group_id` (FK -> groups),
`joined_at`

Notes:
- user-group assignment must stay inside one tenant
- a user's effective permission set is the union of their group's permissions

### audit_events
Fields: `id` (UUID), `actor_id` (FK -> users), `actor_role`, `tenant_id`
(nullable), `action`, `resource_type`, `resource_id`, `outcome`
(`success`/`failure`), `created_at`, `metadata` (JSON blob)

Notes:
- super-admin cross-tenant operations set `tenant_id` to the target tenant when
  applicable
- auth-sensitive mutations must be auditable across all implementations

## Role Hierarchy

- `super_admin` is global, not tenant-scoped. It can create tenants, assign
  the first tenant admin, inspect cross-tenant state, and access only the
  explicit `/admin/*` route surface. Tokens for this role omit `tenant_id`.
- `tenant_admin` is tenant-scoped. It creates groups, invites users, assigns
  catalog permissions to groups, and manages user-group membership within its
  tenant.
- `tenant_member` is tenant-scoped. It acts only through permissions granted by
  groups in the active tenant. The role label helps explain the user but route
  authorization still uses permission atoms.

## The Permission Catalog

All implementations must seed the same permission atoms.

Service: `iam`
- `iam:user:read`
- `iam:user:create`
- `iam:user:update`
- `iam:user:delete`
- `iam:user:invite`
- `iam:group:read`
- `iam:group:create`
- `iam:group:update`
- `iam:group:delete`
- `iam:group:assign_permission`
- `iam:group:assign_user`
- `iam:tenant:read`
- `iam:tenant:create`
- `iam:tenant:update`
- `iam:permission:read`

Service: `billing`
- `billing:invoice:read`
- `billing:invoice:create`
- `billing:subscription:read`
- `billing:subscription:update`

Service: `reports`
- `reports:usage:read`
- `reports:usage:export`
- `reports:audit:read`

Service: `admin`
- `admin:tenant:create`
- `admin:tenant:suspend`
- `admin:audit:read`

The canonical examples in Python, TypeScript, Go, Rust, Java, Kotlin, Ruby,
and Elixir all seed this exact catalog before loading route metadata.

## JWT Claim Shape Standard

All implementations issue short-lived JWT access tokens using this canonical
shape:

```json
{
  "iss": "tenantcore-auth",
  "aud": "tenantcore-api",
  "sub": "<user UUID>",
  "exp": 1735689600,
  "iat": 1735688700,
  "nbf": 1735688700,
  "jti": "<UUID>",
  "tenant_id": "<tenant UUID or null for super_admin>",
  "tenant_role": "tenant_admin | tenant_member | super_admin",
  "groups": ["<group-slug>"],
  "permissions": ["iam:user:read"],
  "acl_ver": 1
}
```

Notes:
- `exp` must be no more than 15 minutes after `iat`
- `permissions` are embedded for fast request-time authorization checks
- `acl_ver` must match `users.acl_ver` or the token is treated as stale
- `tenant_id` is `null` or absent for `super_admin`
- `groups` carries group slugs instead of IDs for human-readable `/me` output
- `RS256` is the preferred signing algorithm; `HS256` is acceptable only in
  constrained test or dev mode

## Canonical Flows

The following flows define the minimum behavioral parity expected in every
language example.

### Flow 1: Issue Token
Actor: any authenticated user
Input: email + password or canonical test credentials
Output: signed JWT matching the canonical claim shape
Permissions: none
Notes: `/auth/token` or `/token` is public for credential exchange only

### Flow 2: GET /me
Actor: any valid token holder
Input: Bearer token
Output: JSON including identity, tenant context, groups, permissions,
`allowed_routes`, and `guide_sections`
Permissions: valid token only
Error: `401` when the token is missing, invalid, expired, or stale

### Flow 3: Super Admin - Create Tenant
Actor: `super_admin`
Input: tenant name, tenant slug, first tenant admin email
Output: new tenant, user, and membership records
Permissions: `admin:tenant:create`
Error: `403` for non-super-admin callers

### Flow 4: Tenant Admin - Create Group
Actor: `tenant_admin`
Input: group name, group slug, optional permission names from catalog
Output: new group in the caller's tenant
Permissions: `iam:group:create`
Error: `403` if tenant role is insufficient; `400` for unknown permissions

### Flow 5: Tenant Admin - Assign Permission to Group
Actor: `tenant_admin`
Input: group ID, permission ID
Output: new `group_permissions` record
Permissions: `iam:group:assign_permission`
Error: `403` when role is insufficient; `404` when the group is outside the
caller tenant

### Flow 6: Tenant Admin - Invite User
Actor: `tenant_admin`
Input: email, display name, initial group slugs
Output: new user, membership, and optional `user_groups` rows
Permissions: `iam:user:invite`
Error: `403` when role is insufficient

### Flow 7: Tenant Admin - Assign User to Group
Actor: `tenant_admin`
Input: user ID and group ID in the same tenant
Output: new `user_groups` record
Permissions: `iam:group:assign_user`
Error: `403` when role is insufficient; `404` when either resource is outside
the tenant

### Flow 8: Tenant Member - Read Users in Tenant
Actor: `tenant_member` with `iam:user:read`
Input: Bearer token
Output: list of users in the active tenant
Permissions: `iam:user:read`
Error: `403` when permission is missing; `401` when the token is invalid

### Flow 9: Cross-Tenant Denial
Actor: `tenant_member` from tenant A
Input: valid token plus request targeting tenant B data
Output: `403`
Purpose: negative test that proves tenant isolation is structural

### Flow 10: Stale ACL Version Denial
Actor: any non-super-admin user with outdated token `acl_ver`
Input: valid but stale token
Output: `401`
Purpose: negative test that proves authorization version invalidation works

## Route Metadata Specification

Every implementation must register these routes in a machine-readable metadata
registry.

| Method | Path | Permission | Tenant Scoped | Super Admin Only | Public | Description |
| --- | --- | --- | --- | --- | --- | --- |
| POST | /auth/token | (none) | false | false | true | Exchange credentials for a JWT |
| GET | /me | (none - valid token) | true | false | false | Return caller identity and discoverability data |
| GET | /users | iam:user:read | true | false | false | List users in the active tenant |
| POST | /users | iam:user:invite | true | false | false | Invite or create a user in the active tenant |
| GET | /users/{id} | iam:user:read | true | false | false | Read one user in the active tenant |
| PATCH | /users/{id} | iam:user:update | true | false | false | Update one user in the active tenant |
| GET | /groups | iam:group:read | true | false | false | List groups in the active tenant |
| POST | /groups | iam:group:create | true | false | false | Create a group in the active tenant |
| POST | /groups/{id}/permissions | iam:group:assign_permission | true | false | false | Assign a catalog permission to a group |
| POST | /groups/{id}/users | iam:group:assign_user | true | false | false | Assign a user to a group |
| GET | /permissions | iam:permission:read | true | false | false | List the platform permission catalog |
| GET | /admin/tenants | admin:tenant:create | false | true | false | List tenants for super-admin workflows |
| POST | /admin/tenants | admin:tenant:create | false | true | false | Create a tenant as super admin |
| GET | /health | (none) | false | false | true | Liveness probe |

Implementations may add routes, but they must not remove or rename any route in
this table.

## /me Response Shape

All implementations must return the same JSON structure for `GET /me`:

```json
{
  "sub": "u-acme-admin-0001",
  "email": "admin@acme.example",
  "display_name": "Acme Admin",
  "tenant_id": "t-acme-0001",
  "tenant_name": "Acme Corp",
  "tenant_role": "tenant_admin",
  "groups": ["iam-admins"],
  "permissions": ["iam:user:read", "iam:user:create", "iam:user:invite"],
  "acl_ver": 1,
  "allowed_routes": [
    {
      "method": "GET",
      "path": "/users",
      "permission": "iam:user:read",
      "description": "List users in the active tenant"
    }
  ],
  "guide_sections": ["User Management", "Billing"],
  "issued_at": "2025-01-01T00:00:00Z",
  "expires_at": "2025-01-01T00:15:00Z"
}
```

Super-admin `/me` rules:
- `tenant_id` is `null`
- `tenant_role` is `super_admin`
- `groups` is empty
- `allowed_routes` includes only explicit `/admin/*` routes and public health
  routes when surfaced

## Fixture Contract

All implementations load the shared fixture corpus from
`examples/canonical-auth/domain/fixtures/` at startup or test time.

Required fixture files:
- `users.json`
- `tenants.json`
- `groups.json`
- `permissions.json`
- `memberships.json`
- `group_permissions.json`
- `user_groups.json`

Fixture guarantees:
- at least 2 tenants
- at least 1 `super_admin` user
- at least 1 `tenant_admin` per tenant
- at least 2 `tenant_member` users in the corpus for tenant-scoped flows
- at least 3 groups across tenants
- at least 10 seeded permissions drawn from the full catalog
- at least 2 `group_permissions` assignments
- at least 2 `user_groups` assignments

The fixture set is deterministic, small enough for in-memory loading, and is
the shared truth for all Python, TypeScript, Go, Rust, Java, Kotlin, Ruby, and
Elixir canonical examples.
