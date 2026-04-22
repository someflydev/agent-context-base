module TenantcoreAuth
  module Registry
    ROUTE_REGISTRY = [
      { method: "POST", path: "/auth/token", permission: nil, tenant_scoped: false, description: "Exchange credentials for a JWT", service: "iam", resource: "token", action: "create", public: true, docs_section: "Authentication" },
      { method: "GET", path: "/me", permission: nil, tenant_scoped: true, description: "Return caller identity and discoverability data", service: "iam", resource: "me", action: "read", public: false, docs_section: "Profile" },
      { method: "GET", path: "/users", permission: "iam:user:read", tenant_scoped: true, description: "List users in the active tenant", service: "iam", resource: "user", action: "read", public: false, docs_section: "User Management" },
      { method: "POST", path: "/users", permission: "iam:user:invite", tenant_scoped: true, description: "Invite or create a user in the active tenant", service: "iam", resource: "user", action: "invite", public: false, docs_section: "User Management" },
      { method: "GET", path: "/users/{id}", permission: "iam:user:read", tenant_scoped: true, description: "Read one user in the active tenant", service: "iam", resource: "user", action: "read", public: false, docs_section: "User Management" },
      { method: "PATCH", path: "/users/{id}", permission: "iam:user:update", tenant_scoped: true, description: "Update one user in the active tenant", service: "iam", resource: "user", action: "update", public: false, docs_section: "User Management" },
      { method: "GET", path: "/groups", permission: "iam:group:read", tenant_scoped: true, description: "List groups in the active tenant", service: "iam", resource: "group", action: "read", public: false, docs_section: "Group Management" },
      { method: "POST", path: "/groups", permission: "iam:group:create", tenant_scoped: true, description: "Create a group in the active tenant", service: "iam", resource: "group", action: "create", public: false, docs_section: "Group Management" },
      { method: "POST", path: "/groups/{id}/permissions", permission: "iam:group:assign_permission", tenant_scoped: true, description: "Assign a catalog permission to a group", service: "iam", resource: "group", action: "assign_permission", public: false, docs_section: "Group Management" },
      { method: "POST", path: "/groups/{id}/users", permission: "iam:group:assign_user", tenant_scoped: true, description: "Assign a user to a group", service: "iam", resource: "group", action: "assign_user", public: false, docs_section: "Group Management" },
      { method: "GET", path: "/permissions", permission: "iam:permission:read", tenant_scoped: true, description: "List the platform permission catalog", service: "iam", resource: "permission", action: "read", public: false, docs_section: "Permission Catalog" },
      { method: "GET", path: "/admin/tenants", permission: "admin:tenant:create", tenant_scoped: false, description: "List tenants for super-admin workflows", service: "admin", resource: "tenant", action: "read", public: false, super_admin_only: true, docs_section: "Platform Admin" },
      { method: "POST", path: "/admin/tenants", permission: "admin:tenant:create", tenant_scoped: false, description: "Create a tenant as super admin", service: "admin", resource: "tenant", action: "create", public: false, super_admin_only: true, docs_section: "Platform Admin" },
      { method: "GET", path: "/health", permission: nil, tenant_scoped: false, description: "Liveness probe", service: "iam", resource: "health", action: "read", public: true, docs_section: "Operations" }
    ].freeze

    module_function

    def get_allowed_routes(auth)
      ROUTE_REGISTRY.filter do |route|
        if route[:public]
          true
        elsif route[:super_admin_only]
          auth.tenant_role == "super_admin" && auth.has_permission?(route[:permission])
        elsif auth.tenant_role == "super_admin"
          false
        elsif route[:permission].nil?
          true
        else
          auth.has_permission?(route[:permission])
        end
      end
    end

    def guide_sections(auth)
      get_allowed_routes(auth).map { |route| route[:docs_section] }.compact.uniq
    end
  end
end
