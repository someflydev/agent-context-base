require "json"

module TenantcoreAuth
  module Routes
    class Auth
      def call(request, store, token_service)
        payload = parse_json(request)
        user = store.get_user_by_email(payload["email"])
        return unauthorized unless user && payload["password"] == "password"

        token = token_service.issue_token(user, store)
        [200, json_headers, [JSON.generate(access_token: token, token_type: "Bearer")]]
      end

      private

      def parse_json(request)
        body = request.body.read
        request.body.rewind
        body.empty? ? {} : JSON.parse(body)
      end

      def unauthorized
        [401, json_headers, [JSON.generate(error: "Unauthorized")]]
      end

      def json_headers
        { "Content-Type" => "application/json" }
      end
    end
  end
end
