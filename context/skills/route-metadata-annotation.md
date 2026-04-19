# Route Metadata Annotation

Use this skill when the task is to add a protected route or audit whether route
policy is fully described in metadata.

## When to Use This Skill

- adding a new protected endpoint
- checking whether protected routes are missing metadata
- aligning `/me` output with transport-level permissions
- designing a route registry for one of the supported auth stacks

## Canonical Metadata Fields

Follow `context/doctrine/route-metadata-registry.md`. The canonical fields are:
`method`, `path`, `permission`, `tenant_scoped`, `description`, `service`,
`resource`, `action`, optional `htmx_target`, optional `docs_section`, optional
`super_admin_only`, and optional `public`.

## Language-Specific Annotation Patterns

| Language | Pattern |
| --- | --- |
| Python | dict registry or decorator argument feeding one registry |
| TypeScript | object adjacent to `router.get()` or `router.post()` |
| Go | struct slice registry |
| Rust | static slice of `RouteMetadata` structs |
| Java | annotation or registry bean |
| Kotlin | `data class` registry list |
| Ruby | hash registry or small DSL |
| Elixir | module attribute list |

## How Middleware Reads the Registry

Match the current request’s method and normalized path against the route
registry, then enforce the declared permission and scope. Do not scatter
permission strings through handlers and middleware branches.

## How /me Reads the Registry

Filter the same registry by effective permissions and tenant scope at request
time, then emit the surviving entries as `allowed_routes`. `/me` should not own
a second visibility map.

## Coverage Check

Add or run a verification step that reads the route registry and confirms that
every referenced permission exists in the permission catalog. Missing metadata
or missing permission atoms should fail verification.

## Anti-Patterns

- inline permission strings in handlers with no shared registry
- keeping a separate `/me` visibility list
- leaving public routes undeclared because they “obviously” need no auth
- referencing permission atoms that are absent from the catalog
