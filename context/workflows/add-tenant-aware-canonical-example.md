# Workflow: Add a Tenant-Aware Canonical Example

## When to Use This Workflow

Use this workflow when a task adds one new language implementation under
`examples/canonical-auth/`.

## Steps

1. Read `examples/canonical-auth/domain/spec.md` in full before writing code.

2. Read `examples/canonical-auth/CATALOG.md` and add a row for the new language
   with status `[ ]`.

3. Create `examples/canonical-auth/<language>/` using the
   `tenant-aware-backend-api` archetype directory shape.

4. Implement JWT middleware using the target language stack file.

5. Implement request-scoped auth context carrying user, tenant, permissions, and
   `acl_ver`.

6. Load fixture data from `examples/canonical-auth/domain/fixtures/` at startup.

7. Implement the routes defined by the shared domain route registry.

8. Implement `/me` with JSON required and HTML recommended when the stack serves
   HTMX-friendly UI.

9. Add smoke tests covering token issuance, RBAC enforcement, `/me`, cross-
   tenant denial, and tenant boundary checks.

10. Update `CATALOG.md` to `[x]` and update
    `examples/canonical-auth/domain/parity-matrix.md` for the new language.
