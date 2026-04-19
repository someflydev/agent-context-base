# RBAC and Permission Taxonomy

## Core Principle

The canonical permission namespace is `{service}:{resource}:{action}`. The
platform owns this namespace and publishes the permission catalog. Tenant-admins
compose groups from that catalog; they do not invent new permission atoms.

## Rules

Rule 1 — Permission atoms follow `{service}:{resource}:{action}`.
Examples include `iam:user:read`, `iam:group:create`,
`billing:invoice:read`, and `reports:usage:export`. Actions should be precise
verbs, but still portable across routes and UI surfaces. Raw URL paths are
never permission identifiers.

Rule 2 — The permission catalog is platform-owned.
The platform decides which permissions exist and what they mean.
Tenant-admins assign cataloged permissions to groups. They cannot create novel
atoms, because tenant-defined atoms invite privilege sprawl and semantic drift.

Rule 3 — RBAC works through group assignment.
Users gain permissions by belonging to groups, and groups hold permission sets.
Tenant-admins manage group composition and membership. Direct per-user
permission assignment is intentionally out of scope because it multiplies policy
maintenance cost and weakens auditability.

Rule 4 — Super-admin is a global role, not a tenant role.
Cross-tenant powers such as tenant creation, tenant-admin assignment, and
cross-tenant inspection belong to a global super-admin construct. Never bury
super-admin behavior inside tenant-local role checks. Tenant auth paths and
super-admin auth paths should stay visibly separate.

Rule 5 — Effective permissions are computed, not stored raw.
The user’s effective permission set is the union of all permissions granted by
their groups in the active tenant. Compute that set at token issuance or on
demand. Do not persist a permanent denormalized permission list as the system of
record.

Rule 6 — Hierarchical role labels are supplemental, not authoritative.
JWT fields like `tenant_role: "admin"` are useful for UI hints, logging, and
coarse explanations. Authorization decisions still use permission atoms.
Role labels are descriptive shortcuts, not the durable policy namespace.

Rule 7 — Permission coverage must be verifiable.
Route metadata must reference permission atoms from the catalog, and the repo
must be able to verify that relationship. A protected route without a cataloged
permission is drift, not flexibility. CI should treat missing coverage as a
defect.

## Anti-Patterns

- permission identifiers that mirror URL paths or HTTP verbs directly
- tenant-admins creating ad hoc permission atoms outside the platform catalog
- attaching permissions directly to users instead of going through groups
- gating routes solely on broad role labels like `admin` or `member`
- letting route metadata reference permissions that are absent from the catalog

## Canonical Permission Catalog (example)

| Service | Resource | Action | Permission atom |
| --- | --- | --- | --- |
| iam | user | read | `iam:user:read` |
| iam | user | invite | `iam:user:invite` |
| iam | user | suspend | `iam:user:suspend` |
| iam | group | read | `iam:group:read` |
| iam | group | create | `iam:group:create` |
| iam | group | update | `iam:group:update` |
| billing | invoice | read | `billing:invoice:read` |
| billing | invoice | approve | `billing:invoice:approve` |
| billing | subscription | update | `billing:subscription:update` |
| reports | usage | read | `reports:usage:read` |
| reports | usage | export | `reports:usage:export` |
| reports | audit-log | read | `reports:audit-log:read` |
