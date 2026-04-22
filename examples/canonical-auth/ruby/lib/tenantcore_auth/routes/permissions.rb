require "json"

require_relative "../auth/rbac_helper"

module TenantcoreAuth
  module Routes
    class Permissions
      def call(request, store, _token_service)
        Auth::RbacHelper.require_permission!(request, "iam:permission:read")
        permissions = store.list_permissions.map do |permission|
          { id: permission.id, name: permission.name, description: permission.description }
        end
        [200, { "Content-Type" => "application/json" }, [JSON.generate(permissions: permissions)]]
      end
    end
  end
end
