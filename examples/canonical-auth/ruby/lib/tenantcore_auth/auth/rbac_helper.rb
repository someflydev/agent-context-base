require "json"

require_relative "jwt_middleware"

module TenantcoreAuth
  module Auth
    module RbacHelper
      module_function

      def auth_context(request)
        request.env[JwtMiddleware::AUTH_CONTEXT_KEY]
      end

      def require_auth!(request)
        auth = auth_context(request)
        return auth if auth

        throw :halt, response(401, error: "Unauthorized")
      end

      def require_permission!(request, permission)
        auth = require_auth!(request)
        return auth if auth.has_permission?(permission)

        throw :halt, response(403, error: "Forbidden")
      end

      def require_super_admin!(request)
        auth = require_auth!(request)
        return auth if auth.tenant_role == "super_admin"

        throw :halt, response(403, error: "Forbidden")
      end

      def response(status, payload)
        [status, { "Content-Type" => "application/json" }, [JSON.generate(payload)]]
      end
    end
  end
end
