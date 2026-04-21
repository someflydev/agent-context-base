import { Hono } from "hono";
import { jwtMiddleware } from "../auth/middleware";
import { AuthContext } from "../auth/context";
import { store } from "../domain/store";
import { getAllowedRoutes } from "../registry/routes";

const app = new Hono();

app.get("/me", jwtMiddleware, async (c) => {
  const auth = c.get("auth") as AuthContext;
  const user = store.getUserById(auth.sub);

  if (!user) {
    return c.json({ error: "User not found" }, 404);
  }

  const tenantName = auth.tenantId ? store.getTenantName(auth.tenantId) : null;
  const isSuperAdmin = auth.tenantRole === "super_admin";
  const allowedRoutes = getAllowedRoutes(auth.permissions, isSuperAdmin);

  const guideSectionsSet = new Set<string>();
  for (const r of allowedRoutes) {
    if (r.description) {
      guideSectionsSet.add(r.description);
    }
  }

  return c.json({
    sub: auth.sub,
    email: auth.email,
    display_name: user.display_name,
    tenant_id: auth.tenantId,
    tenant_name: tenantName,
    tenant_role: auth.tenantRole,
    groups: auth.groups,
    permissions: auth.permissions,
    acl_ver: auth.aclVer,
    allowed_routes: allowedRoutes,
    guide_sections: Array.from(guideSectionsSet),
    issued_at: auth.issuedAt.toISOString().replace(".000Z", "Z"),
    expires_at: auth.expiresAt.toISOString().replace(".000Z", "Z"),
  });
});

export default app;
