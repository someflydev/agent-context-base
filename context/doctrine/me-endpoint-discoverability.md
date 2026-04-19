# /me Endpoint and Auth Discoverability

## Core Principle

The `/me` endpoint is the primary discoverability surface for authentication and
authorization state. A caller should be able to learn who they are, which
tenant they belong to, which groups shape their access, what they can do, and
which routes or UI sections are available. `/me` is not a convenience echo of
JWT claims. It is the self-documenting contract for permission-aware systems.

## Required /me Response Fields

| Field | Type | Description |
| --- | --- | --- |
| sub | string | User subject identifier |
| email | string | User email |
| tenant_id | string | Active tenant identifier |
| tenant_name | string | Active tenant display name |
| tenant_role | string | Broad role label such as `admin` or `member` |
| groups | array | Group slugs or IDs for the active tenant |
| permissions | array | Effective permission atoms |
| acl_ver | int | Current authorization version |
| allowed_routes | array | Route metadata records the caller may access |
| guide_sections | array | Docs or UI sections derived from route metadata |
| issued_at | string | Token issuance time in ISO 8601 form |
| expires_at | string | Token expiry time in ISO 8601 form |

## Rules

Rule 1 — `/me` is computed from validated token claims plus live data.
Identity claims and effective permissions originate from the validated token.
Tenant name, group membership details, and route visibility come from live data
or the route registry at request time. A stale token decode alone is not a
correct `/me` response.

Rule 2 — `allowed_routes` is filtered, not enumerated.
`/me` returns only the routes the caller may access, derived by filtering the
route registry against effective permissions and tenant scope. It must not dump
all routes or all permissions separately and expect the client to reason about
access. Discoverability belongs on the server.

Rule 3 — `guide_sections` supports HTMX-driven UI.
Guide and navigation sections should be derived from the `docs_section` fields
on the filtered route metadata. A server-rendered HTMX navigation surface can
use this list directly. That keeps UI visibility aligned with backend policy.

Rule 4 — `/me` must be protected.
`/me` requires a valid token and returns `401` when authentication is missing or
invalid. It is not a public inspection tool. Anonymous callers do not get a
partial or downgraded response.

Rule 5 — `/me` response is a teaching tool.
Field names should be explicit to a developer seeing the endpoint for the first
time. `allowed_routes.description` values should explain operations in plain
language. Opaque abbreviations make the auth system harder to understand and
harder to debug.

Rule 6 — `/me` may be rendered as HTML as well as JSON.
Canonical auth examples require JSON and may also support an HTMX-friendly HTML
fragment negotiated through `Accept`. The same underlying data model should
power both forms. When HTML exists, it should support profile pages, nav menus,
and capability guides without introducing a second policy list.

## Anti-Patterns

- implementing `/me` as a raw JWT decode echo with no live lookup
- returning `/me` without first validating the token fully
- maintaining a hardcoded `allowed_routes` list outside the route registry
- omitting `guide_sections` when the system exposes permission-aware UI
- supporting only JSON when the backend also serves HTMX-driven UI surfaces

## Navigation

Route metadata registry: `context/doctrine/route-metadata-registry.md`
Domain spec (response shape detail): `examples/canonical-auth/domain/spec.md`
Canonical implementations: `examples/canonical-auth/<language>/`
