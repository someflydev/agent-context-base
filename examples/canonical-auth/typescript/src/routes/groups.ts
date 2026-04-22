import { Hono } from "hono";
import { jwtMiddleware, requirePermission } from "../auth/middleware.ts";
import { store } from "../domain/store.ts";
import type { AuthContext } from "../auth/context.ts";
import type { Group, GroupPermission, UserGroup } from "../domain/models.ts";

const app = new Hono();

app.use("/groups", jwtMiddleware);
app.use("/groups/:id/permissions", jwtMiddleware);
app.use("/groups/:id/users", jwtMiddleware);

app.get("/groups", requirePermission("iam:group:read"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const tenantGroups = store.groups.filter((g) => g.tenant_id === auth.tenantId);
  return c.json({ groups: tenantGroups });
});

app.post("/groups", requirePermission("iam:group:create"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const body = await c.req.json();
  const now = new Date().toISOString().replace(".000Z", "Z");

  if (store.groups.some((g) => g.tenant_id === auth.tenantId && g.slug === body.slug)) {
    return c.json({ detail: "Group slug already exists in tenant" }, 400);
  }

  const groupId = crypto.randomUUID();
  const newGroup: Group = {
    id: groupId,
    tenant_id: auth.tenantId as string,
    slug: body.slug,
    name: body.name,
    created_at: now,
  };
  store.groups.push(newGroup);

  if (body.permissions && Array.isArray(body.permissions)) {
    for (const permName of body.permissions) {
      const perm = store.permissions.find((p) => p.name === permName);
      if (!perm) {
        return c.json({ detail: `Permission ${permName} not found` }, 400);
      }
      store.group_permissions.push({
        id: crypto.randomUUID(),
        group_id: groupId,
        permission_id: perm.id,
        granted_at: now,
      });
    }
  }

  return c.json(newGroup);
});

app.post("/groups/:id/permissions", requirePermission("iam:group:assign_permission"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const groupId = c.req.param("id");
  const body = await c.req.json();

  const group = store.groups.find((g) => g.id === groupId && g.tenant_id === auth.tenantId);
  if (!group) {
    return c.json({ detail: "Group not found in your tenant" }, 404);
  }

  const perm = store.permissions.find((p) => p.id === body.permission_id);
  if (!perm) {
    return c.json({ detail: "Permission not found" }, 400);
  }

  if (store.group_permissions.some((gp) => gp.group_id === groupId && gp.permission_id === perm.id)) {
    return c.json({ status: "ok", message: "Already assigned" });
  }

  const now = new Date().toISOString().replace(".000Z", "Z");
  store.group_permissions.push({
    id: crypto.randomUUID(),
    group_id: groupId,
    permission_id: perm.id,
    granted_at: now,
  });

  for (const ug of store.user_groups) {
    if (ug.group_id === groupId) {
      const user = store.getUserById(ug.user_id);
      if (user) {
        user.acl_ver += 1;
      }
    }
  }

  return c.json({ status: "ok" });
});

app.post("/groups/:id/users", requirePermission("iam:group:assign_user"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const groupId = c.req.param("id");
  const body = await c.req.json();

  const group = store.groups.find((g) => g.id === groupId && g.tenant_id === auth.tenantId);
  if (!group) {
    return c.json({ detail: "Group not found in your tenant" }, 404);
  }

  if (!store.verifyMembership(body.user_id, auth.tenantId as string)) {
    return c.json({ detail: "User not found in your tenant" }, 404);
  }

  if (store.user_groups.some((ug) => ug.group_id === groupId && ug.user_id === body.user_id)) {
    return c.json({ status: "ok", message: "Already assigned" });
  }

  const now = new Date().toISOString().replace(".000Z", "Z");
  store.user_groups.push({
    id: crypto.randomUUID(),
    user_id: body.user_id,
    group_id: groupId,
    joined_at: now,
  });

  const user = store.getUserById(body.user_id);
  if (user) {
    user.acl_ver += 1;
  }

  return c.json({ status: "ok" });
});

export default app;
