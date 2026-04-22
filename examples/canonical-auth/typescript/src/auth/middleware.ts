import { jwtVerify } from "jose";
import { hasPermission } from "./context.ts";
import type { AuthContext } from "./context.ts";
import type { MiddlewareHandler } from "hono";
import { getVerificationKey } from "./token.ts";
import { store } from "../domain/store.ts";

export const jwtMiddleware: MiddlewareHandler = async (c, next) => {
  const authHeader = c.req.header("Authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return c.json({ detail: "Missing or invalid token" }, 401);
  }

  const token = authHeader.split(" ")[1];
  const key = await getVerificationKey();

  let payload;
  try {
    const result = await jwtVerify(token, key, {
      issuer: "tenantcore-auth",
      audience: "tenantcore-api",
    });
    payload = result.payload;
  } catch (err: any) {
    if (err.code === "ERR_JWT_EXPIRED") {
      return c.json({ detail: "Token expired" }, 401);
    }
    return c.json({ detail: "Invalid token" }, 401);
  }

  const userId = payload.sub as string;
  const user = store.getUserById(userId);

  if (!user || !user.is_active) {
    return c.json({ detail: "User not found or inactive" }, 401);
  }

  if (payload.acl_ver !== user.acl_ver) {
    return c.json({ detail: "Token is stale (acl_ver mismatch)" }, 401);
  }

  const tenantId = (payload.tenant_id as string) || null;
  if (tenantId) {
    if (!store.verifyMembership(userId, tenantId)) {
      return c.json({ detail: "Not an active member of the tenant" }, 403);
    }
  }

  const authContext: AuthContext = {
    sub: userId,
    email: user.email,
    tenantId,
    tenantRole: payload.tenant_role as any,
    groups: (payload.groups as string[]) || [],
    permissions: (payload.permissions as string[]) || [],
    aclVer: payload.acl_ver as number,
    issuedAt: new Date((payload.iat as number) * 1000),
    expiresAt: new Date((payload.exp as number) * 1000),
  };

  c.set("auth", authContext);
  await next();
};

export function requirePermission(permission: string): MiddlewareHandler {
  return async (c, next) => {
    const auth = c.get("auth") as AuthContext;
    if (!hasPermission(auth, permission)) {
      return c.json({ error: "Forbidden" }, 403);
    }
    await next();
  };
}

export const requireSuperAdmin: MiddlewareHandler = async (c, next) => {
  const auth = c.get("auth") as AuthContext;
  if (auth.tenantRole !== "super_admin") {
    return c.json({ error: "Forbidden" }, 403);
  }
  await next();
};
