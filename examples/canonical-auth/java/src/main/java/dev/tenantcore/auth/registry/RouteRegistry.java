package dev.tenantcore.auth.registry;

import dev.tenantcore.auth.auth.AuthContext;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class RouteRegistry {

    public static final List<RouteMetadata> ROUTE_REGISTRY = List.of(
        new RouteMetadata("POST", "/auth/token", null, false, "Exchange credentials for a JWT", "iam", "token", "create", true, false, "Authentication"),
        new RouteMetadata("GET", "/me", null, true, "Return caller identity and discoverability data", "iam", "me", "read", false, false, "Profile"),
        new RouteMetadata("GET", "/users", "iam:user:read", true, "List users in the active tenant", "iam", "user", "read", false, false, "User Management"),
        new RouteMetadata("POST", "/users", "iam:user:invite", true, "Invite or create a user in the active tenant", "iam", "user", "invite", false, false, "User Management"),
        new RouteMetadata("GET", "/users/{id}", "iam:user:read", true, "Read one user in the active tenant", "iam", "user", "read", false, false, "User Management"),
        new RouteMetadata("PATCH", "/users/{id}", "iam:user:update", true, "Update one user in the active tenant", "iam", "user", "update", false, false, "User Management"),
        new RouteMetadata("GET", "/groups", "iam:group:read", true, "List groups in the active tenant", "iam", "group", "read", false, false, "Group Management"),
        new RouteMetadata("POST", "/groups", "iam:group:create", true, "Create a group in the active tenant", "iam", "group", "create", false, false, "Group Management"),
        new RouteMetadata("POST", "/groups/{id}/permissions", "iam:group:assign_permission", true, "Assign a catalog permission to a group", "iam", "group", "assign_permission", false, false, "Group Management"),
        new RouteMetadata("POST", "/groups/{id}/users", "iam:group:assign_user", true, "Assign a user to a group", "iam", "group", "assign_user", false, false, "Group Management"),
        new RouteMetadata("GET", "/permissions", "iam:permission:read", true, "List the platform permission catalog", "iam", "permission", "read", false, false, "Permission Catalog"),
        new RouteMetadata("GET", "/admin/tenants", "admin:tenant:create", false, "List tenants for super-admin workflows", "admin", "tenant", "read", false, true, "Platform Admin"),
        new RouteMetadata("POST", "/admin/tenants", "admin:tenant:create", false, "Create a tenant as super admin", "admin", "tenant", "create", false, true, "Platform Admin"),
        new RouteMetadata("GET", "/health", null, false, "Liveness probe", "iam", "health", "read", true, false, "Operations")
    );

    private RouteRegistry() {}

    public static List<RouteMetadata> getAllowedRoutes(AuthContext auth) {
        return ROUTE_REGISTRY.stream()
            .filter(route -> isAllowed(route, auth))
            .toList();
    }

    public static Set<String> getGuideSections(AuthContext auth) {
        return getAllowedRoutes(auth).stream()
            .map(RouteMetadata::docsSection)
            .filter(section -> section != null && !section.isBlank())
            .collect(LinkedHashSet::new, Set::add, Set::addAll);
    }

    private static boolean isAllowed(RouteMetadata route, AuthContext auth) {
        if (route.isPublic()) {
            return true;
        }
        if (route.superAdminOnly()) {
            return "super_admin".equals(auth.tenantRole()) && auth.hasPermission(route.permission());
        }
        if ("super_admin".equals(auth.tenantRole())) {
            return false;
        }
        return route.permission() == null || auth.hasPermission(route.permission());
    }
}
