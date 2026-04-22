require "json"

require_relative "../auth/rbac_helper"

module TenantcoreAuth
  module Routes
    class Users
      def index(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:user:read")
        users = store.list_users(auth.tenant_id).map do |user|
          serialize_user(user)
        end
        [200, json_headers, [JSON.generate(users: users)]]
      end

      def show(request, store, _token_service, id:)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:user:read")
        user = store.get_user_by_id(id)
        return forbidden unless user && user.tenant_id == auth.tenant_id

        [200, json_headers, [JSON.generate(user: serialize_user(user))]]
      end

      def create(request, store, _token_service)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:user:invite")
        payload = parse_json(request)
        user = store.invite_user(
          tenant_id: auth.tenant_id,
          email: payload.fetch("email"),
          display_name: payload.fetch("display_name"),
          group_slugs: payload.fetch("group_slugs", [])
        )
        [201, json_headers, [JSON.generate(user: serialize_user(user))]]
      end

      def update(request, store, _token_service, id:)
        auth = ::TenantcoreAuth::Auth::RbacHelper.require_permission!(request, "iam:user:update")
        user = store.get_user_by_id(id)
        return forbidden unless user && user.tenant_id == auth.tenant_id

        payload = parse_json(request)
        user.display_name = payload["display_name"] if payload["display_name"]
        [200, json_headers, [JSON.generate(user: serialize_user(user))]]
      end

      private

      def parse_json(request)
        body = request.body.read
        request.body.rewind
        body.empty? ? {} : JSON.parse(body)
      end

      def serialize_user(user)
        {
          id: user.id,
          email: user.email,
          display_name: user.display_name,
          tenant_id: user.tenant_id,
          acl_ver: user.acl_ver
        }
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
