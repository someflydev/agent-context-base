export interface AuthContext {
  sub: string;
  email: string;
  tenantId: string | null;
  tenantRole: "super_admin" | "tenant_admin" | "tenant_member";
  groups: string[];
  permissions: string[];
  aclVer: number;
  issuedAt: Date;
  expiresAt: Date;
}

export function hasPermission(ctx: AuthContext, permission: string): boolean {
  return ctx.permissions.includes(permission);
}
