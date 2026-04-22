require "json"

require_relative "../auth/rbac_helper"
require_relative "../registry/route_registry"

module TenantcoreAuth
  module Routes
    class Me
      def call(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_auth!(request)
        tenant_name = auth.tenant_id ? store.get_tenant_name(auth.tenant_id) : nil
        allowed_routes = Registry.get_allowed_routes(auth).map do |route|
          route.slice(:method, :path, :permission, :description)
        end

        payload = {
          sub: auth.sub,
          email: auth.email,
          display_name: store.get_user_by_id(auth.sub)&.display_name,
          tenant_id: auth.tenant_id,
          tenant_name: tenant_name,
          tenant_role: auth.tenant_role,
          groups: auth.groups,
          permissions: auth.permissions,
          acl_ver: auth.acl_ver,
          allowed_routes: allowed_routes,
          guide_sections: Registry.guide_sections(auth),
          issued_at: auth.issued_at.utc.iso8601,
          expires_at: auth.expires_at.utc.iso8601
        }
        [200, json_headers, [JSON.generate(payload)]]
      end

      private

      def json_headers
        { "Content-Type" => "application/json" }
      end
    end
  end
end
