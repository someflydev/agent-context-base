import { Hono } from "hono";
import { jwtMiddleware, requireSuperAdmin } from "../auth/middleware";
import { store } from "../domain/store";
import { Tenant, User } from "../domain/models";

const app = new Hono();

app.use("*", jwtMiddleware, requireSuperAdmin);

app.get("/admin/tenants", async (c) => {
  return c.json({ tenants: store.tenants });
});

app.post("/admin/tenants", async (c) => {
  const body = await c.req.json();
  const now = new Date().toISOString().replace(".000Z", "Z");

  if (store.tenants.some((t) => t.slug === body.slug)) {
    return c.json({ detail: "Tenant slug already exists" }, 400);
  }

  const tenantId = crypto.randomUUID();
  const newTenant: Tenant = {
    id: tenantId,
    slug: body.slug,
    name: body.name,
    is_active: true,
    created_at: now,
  };
  store.tenants.push(newTenant);

  const userId = crypto.randomUUID();
  const newUser: User = {
    id: userId,
    email: body.admin_email,
    display_name: "Admin",
    tenant_id: tenantId,
    is_active: true,
    acl_ver: 1,
    created_at: now,
  };
  store.users.push(newUser);

  store.memberships.push({
    id: crypto.randomUUID(),
    user_id: userId,
    tenant_id: tenantId,
    tenant_role: "tenant_admin",
    is_active: true,
    created_at: now,
  });

  return c.json(newTenant);
});

export default app;
