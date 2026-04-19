# /me Endpoint Design

Use this skill when the task is to add, extend, or audit the `/me`
discoverability endpoint in a JWT-protected service.

## When to Use This Skill

- adding a new `/me` endpoint
- extending `/me` output with route or guide visibility
- deciding whether `/me` should support HTML as well as JSON
- verifying that `/me` stays aligned with route metadata and permissions

## Canonical Response Shape

Follow `context/doctrine/me-endpoint-discoverability.md`. The canonical payload
includes subject identity, tenant identity, broad role label, groups,
permissions, `acl_ver`, `allowed_routes`, `guide_sections`, and token timing
fields. `/me` should explain the caller’s access in plain language.

## Data Sources: Token Claims vs Live DB Lookup

Use validated token claims for `sub`, `tenant_id`, `permissions`, and
authorization timing fields. Use live data for tenant display details, group
membership details, and any state that may have changed since token issuance.
Do not treat a JWT decode as a complete `/me` response.

## `allowed_routes` Computation

Load the route metadata registry, then filter it against the caller’s effective
permissions and tenant scope. Include only the routes the caller may access.
This must be derived, not hand-maintained.

## `guide_sections` Derivation

Collect unique `docs_section` values from the filtered `allowed_routes` list and
return them in a stable order. This lets the backend drive nav menus and guide
surfaces without duplicating policy in UI code.

## JSON vs HTML Variant Decision

JSON is mandatory for API clients and automation. Add an HTML fragment variant
when the backend also serves HTMX-driven profile pages, capability guides, or
nav menus. Use content negotiation or a clear format switch instead of a second
policy list.

## HTMX Rendering Pattern

Treat `/me` as a source for profile summaries, allowed-route guides, and
permission-aware navigation. The same filtered route data that powers JSON
should also power fragment rendering if HTML is supported.

## Testing /me

Verify that `allowed_routes` is exactly the set implied by the effective
permissions. Include tests for tenant mismatch, stale `acl_ver`, and a caller
who has fewer permissions than a tenant-admin.

## Anti-Patterns

- serving `/me` without validating the token fully
- hardcoding route lists separate from the route registry
- exposing opaque field names that do not teach the auth model
- treating `/me` as a raw claims echo with no live state
