package dev.tenantcore.auth.registry

import dev.tenantcore.auth.auth.AuthContext

data class RouteMetadata(
    val method: String,
    val path: String,
    val permission: String?,
    val tenantScoped: Boolean,
    val description: String,
    val service: String,
    val resource: String,
    val action: String,
    val isPublic: Boolean = false,
    val superAdminOnly: Boolean = false,
    val docsSection: String? = null,
)

val routeRegistry: List<RouteMetadata> = listOf(
    RouteMetadata("POST", "/auth/token", null, false, "Exchange credentials for a JWT", "iam", "token", "create", isPublic = true, docsSection = "Authentication"),
    RouteMetadata("GET", "/me", null, true, "Return caller identity and discoverability data", "iam", "me", "read", docsSection = "Profile"),
    RouteMetadata("GET", "/users", "iam:user:read", true, "List users in the active tenant", "iam", "user", "read", docsSection = "User Management"),
    RouteMetadata("POST", "/users", "iam:user:invite", true, "Invite or create a user in the active tenant", "iam", "user", "invite", docsSection = "User Management"),
    RouteMetadata("GET", "/users/{id}", "iam:user:read", true, "Read one user in the active tenant", "iam", "user", "read", docsSection = "User Management"),
    RouteMetadata("PATCH", "/users/{id}", "iam:user:update", true, "Update one user in the active tenant", "iam", "user", "update", docsSection = "User Management"),
    RouteMetadata("GET", "/groups", "iam:group:read", true, "List groups in the active tenant", "iam", "group", "read", docsSection = "Group Management"),
    RouteMetadata("POST", "/groups", "iam:group:create", true, "Create a group in the active tenant", "iam", "group", "create", docsSection = "Group Management"),
    RouteMetadata("POST", "/groups/{id}/permissions", "iam:group:assign_permission", true, "Assign a catalog permission to a group", "iam", "group", "assign_permission", docsSection = "Group Management"),
    RouteMetadata("POST", "/groups/{id}/users", "iam:group:assign_user", true, "Assign a user to a group", "iam", "group", "assign_user", docsSection = "Group Management"),
    RouteMetadata("GET", "/permissions", "iam:permission:read", true, "List the platform permission catalog", "iam", "permission", "read", docsSection = "Permission Catalog"),
    RouteMetadata("GET", "/admin/tenants", "admin:tenant:create", false, "List tenants for super-admin workflows", "admin", "tenant", "read", superAdminOnly = true, docsSection = "Platform Admin"),
    RouteMetadata("POST", "/admin/tenants", "admin:tenant:create", false, "Create a tenant as super admin", "admin", "tenant", "create", superAdminOnly = true, docsSection = "Platform Admin"),
    RouteMetadata("GET", "/health", null, false, "Liveness probe", "iam", "health", "read", isPublic = true, docsSection = "Operations"),
)

fun getAllowedRoutes(auth: AuthContext): List<RouteMetadata> = routeRegistry.filter { route ->
    when {
        route.isPublic -> true
        route.superAdminOnly -> auth.tenantRole == "super_admin" && route.permission?.let(auth::hasPermission) == true
        auth.tenantRole == "super_admin" -> false
        route.permission == null -> true
        else -> auth.hasPermission(route.permission)
    }
}

fun getGuideSections(auth: AuthContext): List<String> =
    getAllowedRoutes(auth).mapNotNull { it.docsSection }.distinct()
