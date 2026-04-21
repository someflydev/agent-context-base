export interface RouteMetadata {
  method: string;
  path: string;
  permission: string | null;
  tenant_scoped: boolean;
  super_admin_only: boolean;
  public: boolean;
  description: string;
}

export const ROUTE_REGISTRY: RouteMetadata[] = [
  { method: "POST", path: "/auth/token", permission: null, tenant_scoped: false, super_admin_only: false, public: true, description: "Exchange credentials for a JWT" },
  { method: "GET", path: "/me", permission: null, tenant_scoped: true, super_admin_only: false, public: false, description: "Return caller identity and discoverability data" },
  { method: "GET", path: "/users", permission: "iam:user:read", tenant_scoped: true, super_admin_only: false, public: false, description: "List users in the active tenant" },
  { method: "POST", path: "/users", permission: "iam:user:invite", tenant_scoped: true, super_admin_only: false, public: false, description: "Invite or create a user in the active tenant" },
  { method: "GET", path: "/users/:id", permission: "iam:user:read", tenant_scoped: true, super_admin_only: false, public: false, description: "Read one user in the active tenant" },
  { method: "PATCH", path: "/users/:id", permission: "iam:user:update", tenant_scoped: true, super_admin_only: false, public: false, description: "Update one user in the active tenant" },
  { method: "GET", path: "/groups", permission: "iam:group:read", tenant_scoped: true, super_admin_only: false, public: false, description: "List groups in the active tenant" },
  { method: "POST", path: "/groups", permission: "iam:group:create", tenant_scoped: true, super_admin_only: false, public: false, description: "Create a group in the active tenant" },
  { method: "POST", path: "/groups/:id/permissions", permission: "iam:group:assign_permission", tenant_scoped: true, super_admin_only: false, public: false, description: "Assign a catalog permission to a group" },
  { method: "POST", path: "/groups/:id/users", permission: "iam:group:assign_user", tenant_scoped: true, super_admin_only: false, public: false, description: "Assign a user to a group" },
  { method: "GET", path: "/permissions", permission: "iam:permission:read", tenant_scoped: true, super_admin_only: false, public: false, description: "List the platform permission catalog" },
  { method: "GET", path: "/admin/tenants", permission: "admin:tenant:create", tenant_scoped: false, super_admin_only: true, public: false, description: "List tenants for super-admin workflows" },
  { method: "POST", path: "/admin/tenants", permission: "admin:tenant:create", tenant_scoped: false, super_admin_only: true, public: false, description: "Create a tenant as super admin" },
  { method: "GET", path: "/health", permission: null, tenant_scoped: false, super_admin_only: false, public: true, description: "Liveness probe" }
];

export function getAllowedRoutes(permissions: string[], isSuperAdmin = false): RouteMetadata[] {
  return ROUTE_REGISTRY.filter((route) => {
    if (route.public) return true;
    if (isSuperAdmin && route.super_admin_only) return true;
    if (!isSuperAdmin && route.permission && permissions.includes(route.permission)) return true;
    if (!isSuperAdmin && route.path === "/me") return true;
    return false;
  });
}
