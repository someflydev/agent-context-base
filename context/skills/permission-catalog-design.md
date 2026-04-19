# Permission Catalog Design

Use this skill when the task is to define, extend, or audit the platform-owned
permission catalog for a JWT and RBAC system.

## When to Use This Skill

- defining new permission atoms
- expanding a service’s permission coverage
- reviewing whether route permissions are named coherently
- deciding what belongs in the platform catalog versus tenant-admin composition

## `{service}:{resource}:{action}` Formula

Permission atoms use the form `{service}:{resource}:{action}`. Good examples:
`iam:user:read`, `iam:group:create`, `billing:invoice:approve`,
`reports:usage:export`. The service names the business subdomain, the resource
names the thing being acted on, and the action names the durable verb.

## How to Determine Service Boundaries

Use one service label per business subdomain, not per route prefix or controller
class. `iam`, `billing`, and `reports` are good service boundaries because they
survive transport refactors. Avoid letting one service label drift into many
micro-categories unless the domain is truly separate.

## How to Choose Action Verbs

Prefer durable verbs such as `read`, `create`, `update`, `delete`, `export`,
`invite`, and `approve`. Add a more specific verb only when it represents a
stable business capability rather than a one-off route. Action names should
teach policy, not mirror controller method names mechanically.

## What Belongs in the Catalog vs Tenant-Admin Composition

The platform-owned catalog defines which atoms exist and what they mean.
Tenant-admins compose groups from those atoms and assign users to those groups.
Tenant-admins do not create novel atoms, because permission invention belongs to
platform policy design, not tenant-local configuration.

## Catalog Evolution

Adding a permission atom is usually safe when new capability is introduced.
Removing or renaming an atom requires a migration plan because groups, docs, and
route metadata may already depend on it. Treat catalog changes as API changes
for authorization semantics.

## Coverage Check

Collect every permission referenced by the route metadata registry and verify
that each atom exists in the catalog. Fail verification if any protected route
references a missing atom. Coverage checks prevent silent policy drift.

## Anti-Patterns

- using URL paths or HTTP verbs as permission identifiers
- letting tenant-admins define new permission atoms
- exploding the action vocabulary into route-specific one-offs
- storing policy only in group labels instead of durable permission atoms
