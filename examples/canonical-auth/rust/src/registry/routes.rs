use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct RouteMetadata {
    pub method: &'static str,
    pub path: &'static str,
    pub permission: &'static str,
    pub tenant_scoped: bool,
    pub description: &'static str,
    pub service: &'static str,
    pub resource: &'static str,
    pub action: &'static str,
    pub public: bool,
    pub super_admin_only: bool,
}

pub static ROUTE_REGISTRY: &[RouteMetadata] = &[
    RouteMetadata {
        method: "POST",
        path: "/auth/token",
        permission: "",
        tenant_scoped: false,
        description: "Exchange credentials for a JWT",
        service: "",
        resource: "",
        action: "",
        public: true,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "GET",
        path: "/me",
        permission: "",
        tenant_scoped: true,
        description: "Return caller identity and discoverability data",
        service: "",
        resource: "",
        action: "",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "GET",
        path: "/users",
        permission: "iam:user:read",
        tenant_scoped: true,
        description: "List users in the active tenant",
        service: "iam",
        resource: "user",
        action: "read",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "POST",
        path: "/users",
        permission: "iam:user:invite",
        tenant_scoped: true,
        description: "Invite or create a user in the active tenant",
        service: "iam",
        resource: "user",
        action: "invite",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "GET",
        path: "/users/{id}",
        permission: "iam:user:read",
        tenant_scoped: true,
        description: "Read one user in the active tenant",
        service: "iam",
        resource: "user",
        action: "read",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "PATCH",
        path: "/users/{id}",
        permission: "iam:user:update",
        tenant_scoped: true,
        description: "Update one user in the active tenant",
        service: "iam",
        resource: "user",
        action: "update",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "GET",
        path: "/groups",
        permission: "iam:group:read",
        tenant_scoped: true,
        description: "List groups in the active tenant",
        service: "iam",
        resource: "group",
        action: "read",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "POST",
        path: "/groups",
        permission: "iam:group:create",
        tenant_scoped: true,
        description: "Create a group in the active tenant",
        service: "iam",
        resource: "group",
        action: "create",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "POST",
        path: "/groups/{id}/permissions",
        permission: "iam:group:assign_permission",
        tenant_scoped: true,
        description: "Assign a catalog permission to a group",
        service: "iam",
        resource: "group",
        action: "assign_permission",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "POST",
        path: "/groups/{id}/users",
        permission: "iam:group:assign_user",
        tenant_scoped: true,
        description: "Assign a user to a group",
        service: "iam",
        resource: "group",
        action: "assign_user",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "GET",
        path: "/permissions",
        permission: "iam:permission:read",
        tenant_scoped: true,
        description: "List the platform permission catalog",
        service: "iam",
        resource: "permission",
        action: "read",
        public: false,
        super_admin_only: false,
    },
    RouteMetadata {
        method: "GET",
        path: "/admin/tenants",
        permission: "admin:tenant:create",
        tenant_scoped: false,
        description: "List tenants for super-admin workflows",
        service: "admin",
        resource: "tenant",
        action: "create",
        public: false,
        super_admin_only: true,
    },
    RouteMetadata {
        method: "POST",
        path: "/admin/tenants",
        permission: "admin:tenant:create",
        tenant_scoped: false,
        description: "Create a tenant as super admin",
        service: "admin",
        resource: "tenant",
        action: "create",
        public: false,
        super_admin_only: true,
    },
    RouteMetadata {
        method: "GET",
        path: "/health",
        permission: "",
        tenant_scoped: false,
        description: "Liveness probe",
        service: "",
        resource: "",
        action: "",
        public: true,
        super_admin_only: false,
    },
];

pub fn get_allowed_routes(permissions: &[String], is_super_admin: bool) -> Vec<&'static RouteMetadata> {
    let mut allowed = Vec::new();
    for route in ROUTE_REGISTRY {
        if is_super_admin {
            if route.super_admin_only || (route.public && route.path == "/health") {
                allowed.push(route);
            }
        } else {
            if !route.super_admin_only && !route.public {
                if route.permission.is_empty() || permissions.iter().any(|p| p == route.permission) {
                    allowed.push(route);
                }
            }
        }
    }
    allowed
}
