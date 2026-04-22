require "json"

require_relative "../auth/rbac_helper"

module TenantcoreAuth
  module Routes
    class Admin
      def index(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_super_admin!(request)
        return forbidden unless auth.has_permission?("admin:tenant:create")

        tenants = store.list_tenants.map { |tenant| { id: tenant.id, slug: tenant.slug, name: tenant.name } }
        [200, json_headers, [JSON.generate(tenants: tenants)]]
      end

      def create(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_super_admin!(request)
        return forbidden unless auth.has_permission?("admin:tenant:create")

        payload = parse_json(request)
        tenant = store.create_tenant(
          slug: payload.fetch("slug"),
          name: payload.fetch("name"),
          first_admin_email: payload.fetch("first_admin_email")
        )
        [201, json_headers, [JSON.generate(tenant: { id: tenant.id, slug: tenant.slug, name: tenant.name })]]
      end

      private

      def parse_json(request)
        body = request.body.read
        request.body.rewind
        body.empty? ? {} : JSON.parse(body)
      end

      def forbidden
        [403, json_headers, [JSON.generate(error: "Forbidden")]]
      end

      def json_headers
        { "Content-Type" => "application/json" }
      end
    end
  end
end
