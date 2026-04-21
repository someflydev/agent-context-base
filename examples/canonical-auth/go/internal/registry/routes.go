package registry

type RouteMetadata struct {
	Method         string `json:"method"`
	Path           string `json:"path"`
	Permission     string `json:"permission,omitempty"`
	TenantScoped   bool   `json:"tenant_scoped"`
	Description    string `json:"description"`
	Service        string `json:"service,omitempty"`
	Resource       string `json:"resource,omitempty"`
	Action         string `json:"action,omitempty"`
	Public         bool   `json:"public,omitempty"`
	SuperAdminOnly bool   `json:"super_admin_only,omitempty"`
}

var ROUTE_REGISTRY = []RouteMetadata{
	{
		Method:       "POST",
		Path:         "/auth/token",
		Permission:   "",
		TenantScoped: false,
		Description:  "Exchange credentials for a JWT",
		Public:       true,
	},
	{
		Method:       "GET",
		Path:         "/me",
		Permission:   "",
		TenantScoped: true,
		Description:  "Return caller identity and discoverability data",
	},
	{
		Method:       "GET",
		Path:         "/users",
		Permission:   "iam:user:read",
		TenantScoped: true,
		Description:  "List users in the active tenant",
	},
	{
		Method:       "POST",
		Path:         "/users",
		Permission:   "iam:user:invite",
		TenantScoped: true,
		Description:  "Invite or create a user in the active tenant",
	},
	{
		Method:       "GET",
		Path:         "/users/{id}",
		Permission:   "iam:user:read",
		TenantScoped: true,
		Description:  "Read one user in the active tenant",
	},
	{
		Method:       "PATCH",
		Path:         "/users/{id}",
		Permission:   "iam:user:update",
		TenantScoped: true,
		Description:  "Update one user in the active tenant",
	},
	{
		Method:       "GET",
		Path:         "/groups",
		Permission:   "iam:group:read",
		TenantScoped: true,
		Description:  "List groups in the active tenant",
	},
	{
		Method:       "POST",
		Path:         "/groups",
		Permission:   "iam:group:create",
		TenantScoped: true,
		Description:  "Create a group in the active tenant",
	},
	{
		Method:       "POST",
		Path:         "/groups/{id}/permissions",
		Permission:   "iam:group:assign_permission",
		TenantScoped: true,
		Description:  "Assign a catalog permission to a group",
	},
	{
		Method:       "POST",
		Path:         "/groups/{id}/users",
		Permission:   "iam:group:assign_user",
		TenantScoped: true,
		Description:  "Assign a user to a group",
	},
	{
		Method:       "GET",
		Path:         "/permissions",
		Permission:   "iam:permission:read",
		TenantScoped: true,
		Description:  "List the platform permission catalog",
	},
	{
		Method:       "GET",
		Path:         "/admin/tenants",
		Permission:   "admin:tenant:create",
		TenantScoped: false,
		Description:  "List tenants for super-admin workflows",
		SuperAdminOnly: true,
	},
	{
		Method:       "POST",
		Path:         "/admin/tenants",
		Permission:   "admin:tenant:create",
		TenantScoped: false,
		Description:  "Create a tenant as super admin",
		SuperAdminOnly: true,
	},
	{
		Method:       "GET",
		Path:         "/health",
		Permission:   "",
		TenantScoped: false,
		Description:  "Liveness probe",
		Public:       true,
	},
}

func GetAllowedRoutes(permissions []string, isSuperAdmin bool) []RouteMetadata {
	permSet := make(map[string]bool)
	for _, p := range permissions {
		permSet[p] = true
	}

	var allowed []RouteMetadata
	for _, route := range ROUTE_REGISTRY {
		if isSuperAdmin {
			if route.SuperAdminOnly || (route.Public && route.Path == "/health") {
				allowed = append(allowed, route)
			}
		} else {
			if !route.SuperAdminOnly && !route.Public {
				if route.Permission == "" || permSet[route.Permission] {
					allowed = append(allowed, route)
				}
			}
		}
	}
	return allowed
}
