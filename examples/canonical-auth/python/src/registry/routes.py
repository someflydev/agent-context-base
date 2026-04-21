ROUTE_REGISTRY = [
    {"method": "POST", "path": "/auth/token", "permission": None, "tenant_scoped": False, "super_admin_only": False, "public": True, "description": "Exchange credentials for a JWT"},
    {"method": "GET", "path": "/me", "permission": None, "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Return caller identity and discoverability data"},
    {"method": "GET", "path": "/users", "permission": "iam:user:read", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "List users in the active tenant"},
    {"method": "POST", "path": "/users", "permission": "iam:user:invite", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Invite or create a user in the active tenant"},
    {"method": "GET", "path": "/users/{id}", "permission": "iam:user:read", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Read one user in the active tenant"},
    {"method": "PATCH", "path": "/users/{id}", "permission": "iam:user:update", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Update one user in the active tenant"},
    {"method": "GET", "path": "/groups", "permission": "iam:group:read", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "List groups in the active tenant"},
    {"method": "POST", "path": "/groups", "permission": "iam:group:create", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Create a group in the active tenant"},
    {"method": "POST", "path": "/groups/{id}/permissions", "permission": "iam:group:assign_permission", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Assign a catalog permission to a group"},
    {"method": "POST", "path": "/groups/{id}/users", "permission": "iam:group:assign_user", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "Assign a user to a group"},
    {"method": "GET", "path": "/permissions", "permission": "iam:permission:read", "tenant_scoped": True, "super_admin_only": False, "public": False, "description": "List the platform permission catalog"},
    {"method": "GET", "path": "/admin/tenants", "permission": "admin:tenant:create", "tenant_scoped": False, "super_admin_only": True, "public": False, "description": "List tenants for super-admin workflows"},
    {"method": "POST", "path": "/admin/tenants", "permission": "admin:tenant:create", "tenant_scoped": False, "super_admin_only": True, "public": False, "description": "Create a tenant as super admin"},
    {"method": "GET", "path": "/health", "permission": None, "tenant_scoped": False, "super_admin_only": False, "public": True, "description": "Liveness probe"}
]

def get_allowed_routes(permissions: list[str], is_super_admin: bool = False) -> list[dict]:
    allowed = []
    for route in ROUTE_REGISTRY:
        if route["public"]:
            allowed.append(route)
            continue
            
        if is_super_admin and route["super_admin_only"]:
            allowed.append(route)
            continue

        if not is_super_admin and route["permission"] in permissions:
            allowed.append(route)
            continue
            
        # special case for /me which needs no permission but is not public
        if route["path"] == "/me" and not is_super_admin:
            allowed.append(route)
            
    return allowed
