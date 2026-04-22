require "json"

require_relative "auth_context"
require_relative "token_service"

module TenantcoreAuth
  module Auth
    class JwtMiddleware
      AUTH_CONTEXT_KEY = "tenantcore.auth_context".freeze

      def initialize(app, store:, token_service:)
        @app = app
        @store = store
        @token_service = token_service
      end

      def call(env)
        token = extract_token(env)
        if token.nil?
          env[AUTH_CONTEXT_KEY] = nil
          return @app.call(env)
        end

        begin
          payload = @token_service.verify_token(token)
          user = @store.get_user_by_id(payload["sub"])
          return unauthorized unless user&.is_active
          return unauthorized if payload["acl_ver"] != user.acl_ver

          tenant_id = payload["tenant_id"]
          if tenant_id && !@store.verify_membership(user.id, tenant_id)
            return forbidden
          end

          env[AUTH_CONTEXT_KEY] = AuthContext.new(
            sub: payload["sub"],
            email: user.email,
            tenant_id: tenant_id,
            tenant_role: payload["tenant_role"],
            groups: payload["groups"] || [],
            permissions: payload["permissions"] || [],
            acl_ver: payload["acl_ver"],
            issued_at: Time.at(payload["iat"]).utc,
            expires_at: Time.at(payload["exp"]).utc
          )
          @app.call(env)
        rescue JWT::DecodeError, JWT::VerificationError, JWT::ExpiredSignature
          unauthorized
        end
      end

      private

      def extract_token(env)
        header = env["HTTP_AUTHORIZATION"]
        return nil unless header&.start_with?("Bearer ")

        header.delete_prefix("Bearer ").strip
      end

      def unauthorized
        [401, json_headers, [JSON.generate(error: "Unauthorized")]]
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
