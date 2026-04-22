require "json"

require_relative "../auth/rbac_helper"

module TenantcoreAuth
  module Routes
    class Groups
      def index(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:group:read")
        groups = store.list_groups(auth.tenant_id).map { |group| serialize_group(group) }
        [200, json_headers, [JSON.generate(groups: groups)]]
      end

      def create(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:group:create")
        payload = parse_json(request)
        unknown_permissions = payload.fetch("permission_names", []).reject { |name| store.get_permission_by_name(name) }
        return [400, json_headers, [JSON.generate(error: "Unknown permissions", names: unknown_permissions)]] unless unknown_permissions.empty?

        group = store.create_group(
          tenant_id: auth.tenant_id,
          slug: payload.fetch("slug"),
          name: payload.fetch("name"),
          permission_names: payload.fetch("permission_names", [])
        )
        [201, json_headers, [JSON.generate(group: serialize_group(group))]]
      end

      def assign_permission(request, store, _token_service, id:)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:group:assign_permission")
        payload = parse_json(request)
        result = store.assign_permission_to_group(id, payload.fetch("permission"), auth.tenant_id)
        return forbidden unless result

        [201, json_headers, [JSON.generate(status: "assigned")]]
      end

      def assign_user(request, store, _token_service, id:)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:group:assign_user")
        payload = parse_json(request)
        result = store.assign_user_to_group(id, payload.fetch("user_id"), auth.tenant_id)
        return forbidden unless result

        [201, json_headers, [JSON.generate(status: "assigned")]]
      end

      private

      def parse_json(request)
        body = request.body.read
        request.body.rewind
        body.empty? ? {} : JSON.parse(body)
      end

      def serialize_group(group)
        { id: group.id, tenant_id: group.tenant_id, slug: group.slug, name: group.name }
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
