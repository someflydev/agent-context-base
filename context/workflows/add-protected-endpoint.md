# Workflow: Add a Protected Endpoint

## When to Use This Workflow

Use this workflow when a task adds one JWT-protected endpoint to a canonical
auth example or a repo following the same pattern.

## Steps

1. Define the permission atom.
   Most common mistake: inventing a route-shaped permission instead of a
   cataloged `{service}:{resource}:{action}` atom.

2. Add the route metadata record to the registry.
   Most common mistake: registering the route path but omitting
   `tenant_scoped`, `description`, or `docs_section`.

3. Implement the handler.
   Most common mistake: reading raw claims directly instead of receiving the
   request-scoped auth context.

4. Add the route to the framework router.
   Most common mistake: mounting the handler outside the existing protected
   middleware group.

5. Write a test for valid token plus required permission resulting in `200`.
   Most common mistake: testing only the handler helper and not a real request.

6. Write a test for valid token without the required permission resulting in
   `403`.
   Most common mistake: returning `401` when the token is valid but the caller
   is underprivileged.

7. Write a test for missing token resulting in `401`.
   Most common mistake: forgetting the missing-token path because the example
   only covers expired or malformed tokens.

8. Run `python3 scripts/run_verification.py --tier fast` and confirm no
   regression.
   Most common mistake: stopping at targeted tests and missing a repo-level
   contract break.
