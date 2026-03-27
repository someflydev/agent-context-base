## Hono + Bun Constraints

Keep route files narrow and treat request or fragment rendering contracts as explicit surface area. Bun-specific runtime conveniences are acceptable only when they do not obscure route ownership or testability.

Prefer clear route modules and request harnesses over implicit framework magic.
