require "json"

module TenantcoreAuth
  module Routes
    class Health
      def call(_request, _store, _token_service)
        [200, { "Content-Type" => "application/json" }, [JSON.generate(status: "ok")]]
      end
    end
  end
end
