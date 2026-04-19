# Route Metadata Registry

## Core Principle

Every protected route needs a machine-readable metadata record describing the
required permission, tenant scope, and documentation surface. Route metadata is
the durable contract between policy and implementation. Middleware, docs,
coverage checks, and `/me` all read from the same registry. If route policy is
only in inline handler code, the system will drift.

## Canonical Metadata Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| method | string | yes | HTTP method such as `GET` or `POST` |
| path | string | yes | Route path pattern |
| permission | string | yes | Required permission atom |
| tenant_scoped | bool | yes | Whether tenant isolation is enforced |
| description | string | yes | Human-readable operation description |
| service | string | yes | Owning service name |
| resource | string | yes | Resource category |
| action | string | yes | Action verb |
| htmx_target | string | no | HTMX target selector when applicable |
| docs_section | string | no | Guide or docs section label |
| super_admin_only | bool | no | Explicit cross-tenant super-admin gate |
| public | bool | no | Explicit public route opt-in |

## Rules

Rule 1 — Metadata is the single source of truth for route auth requirements.
Middleware and handler guards must read from the route registry, not from
scattered inline permission strings. A route’s required permission is declared
once in metadata and then enforced consistently. The registry is the policy map
for the transport surface.

Rule 2 — Every protected route has exactly one required permission.
Routes that appear to need multiple simultaneous permissions are usually hiding
an underspecified business capability. Model a higher-level permission atom
instead. One route, one permission requirement keeps `/me` output and docs
explanations clear.

Rule 3 — Public routes are explicitly declared, not implicitly assumed.
A missing registry entry is a defect, not a signal that the route must be
public. Public routes must still be listed with `public: true` so verification
can distinguish intentional openness from missing metadata. Silence is not a
policy.

Rule 4 — Route metadata powers `/me` output.
The `/me` handler derives `allowed_routes` by filtering the registry against the
caller’s effective permissions and tenant scope. It must not maintain a second
hardcoded list of visible routes. Discoverability and enforcement read from the
same contract.

Rule 5 — Metadata enables a coverage check.
Verification should be able to read the route registry, extract referenced
permission atoms, and confirm each exists in the platform permission catalog.
Registry entries pointing at unknown permissions are policy drift. The coverage
check belongs in CI, not in a human memory note.

Rule 6 — `htmx_target` documents backend-to-frontend contracts.
When a route serves HTMX fragments, the registry should declare the DOM selector
or fragment target it is expected to update. This keeps server-rendered UI
contracts visible and testable. HTMX behavior should not be left to template
guesswork.

## Anti-Patterns

- inline permission strings inside handlers instead of one shared registry
- public routes that exist only because metadata was omitted
- routes referencing permission atoms that are absent from the catalog
- building `/me` from a second hardcoded list unrelated to route metadata
- HTMX fragment routes with undocumented target selectors or docs sections

## Navigation

The canonical implementation of route metadata in each language lives under
`examples/canonical-auth/<language>/`.
The shared route metadata spec lives in `examples/canonical-auth/domain/spec.md`.
