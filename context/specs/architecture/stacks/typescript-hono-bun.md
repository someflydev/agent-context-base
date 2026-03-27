---
acb_origin: canonical
acb_source_path: context/specs/architecture/stacks/typescript-hono-bun.md
acb_role: architecture
acb_stacks: [typescript-hono-bun]
acb_version: 1
---

## Hono + Bun Constraints

Keep route files narrow and treat request or fragment rendering contracts as explicit surface area. Bun-specific runtime conveniences are acceptable only when they do not obscure route ownership or testability.

Prefer clear route modules and request harnesses over implicit framework magic.
