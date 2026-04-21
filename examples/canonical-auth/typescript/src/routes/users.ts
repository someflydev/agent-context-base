import { Hono } from "hono";
import { jwtMiddleware, requirePermission } from "../auth/middleware";
import { store } from "../domain/store";
import { AuthContext } from "../auth/context";
import { User, Membership, UserGroup } from "../domain/models";

const app = new Hono();

app.use("*", jwtMiddleware);

app.get("/users", requirePermission("iam:user:read"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const tenantUsers = store.users.filter((u) => {
    if (u.tenant_id === auth.tenantId) return true;
    return store.memberships.some(
      (m) => m.user_id === u.id && m.tenant_id === auth.tenantId && m.is_active
    );
  });
  return c.json({ users: tenantUsers });
});

app.post("/users", requirePermission("iam:user:invite"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const body = await c.req.json();
  const now = new Date().toISOString().replace(".000Z", "Z");

  const existingUser = store.getUserByEmail(body.email);
  if (existingUser) {
    if (existingUser.tenant_id === auth.tenantId) {
      return c.json({ detail: "User already in tenant" }, 400);
    }
    return c.json({ detail: "User email already taken globally" }, 400);
  }

  const userId = crypto.randomUUID();
  const newUser: User = {
    id: userId,
    email: body.email,
    display_name: body.display_name,
    tenant_id: auth.tenantId,
    is_active: true,
    acl_ver: 1,
    created_at: now,
  };
  store.users.push(newUser);

  store.memberships.push({
    id: crypto.randomUUID(),
    user_id: userId,
    tenant_id: auth.tenantId as string,
    tenant_role: "tenant_member",
    is_active: true,
    created_at: now,
  });

  if (body.group_slugs && Array.isArray(body.group_slugs)) {
    for (const slug of body.group_slugs) {
      const group = store.groups.find(
        (g) => g.tenant_id === auth.tenantId && g.slug === slug
      );
      if (group) {
        store.user_groups.push({
          id: crypto.randomUUID(),
          user_id: userId,
          group_id: group.id,
          joined_at: now,
        });
      }
    }
  }

  return c.json(newUser);
});

app.get("/users/:id", requirePermission("iam:user:read"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const userId = c.req.param("id");

  const user = store.getUserById(userId);
  if (!user) {
    return c.json({ detail: "User not found" }, 404);
  }
  if (!store.verifyMembership(userId, auth.tenantId as string)) {
    return c.json({ detail: "Forbidden: User not in your tenant" }, 403);
  }
  return c.json(user);
});

app.patch("/users/:id", requirePermission("iam:user:update"), async (c) => {
  const auth = c.get("auth") as AuthContext;
  const userId = c.req.param("id");
  const body = await c.req.json();

  const user = store.getUserById(userId);
  if (!user) {
    return c.json({ detail: "User not found" }, 404);
  }
  if (!store.verifyMembership(userId, auth.tenantId as string)) {
    return c.json({ detail: "Forbidden: User not in your tenant" }, 403);
  }

  if (body.display_name !== undefined) {
    user.display_name = body.display_name;
  }
  if (body.is_active !== undefined) {
    user.is_active = body.is_active;
  }

  user.acl_ver += 1;
  return c.json(user);
});

export default app;
