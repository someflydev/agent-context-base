require "json"
require "rack"

require_relative "auth/jwt_middleware"
require_relative "auth/token_service"
require_relative "domain/in_memory_store"
require_relative "routes/admin"
require_relative "routes/auth"
require_relative "routes/groups"
require_relative "routes/health"
require_relative "routes/me"
require_relative "routes/permissions"
require_relative "routes/users"

module TenantcoreAuth
  class App
    def self.rack_app
      store = Domain::InMemoryStore.load_from_fixtures
      token_service = Auth::TokenService.new
      dispatcher = new(store: store, token_service: token_service)
      Auth::JwtMiddleware.new(dispatcher, store: store, token_service: token_service)
    end

    def initialize(store:, token_service:)
      @store = store
      @token_service = token_service
      @auth_route = Routes::Auth.new
      @me_route = Routes::Me.new
      @users_route = Routes::Users.new
      @groups_route = Routes::Groups.new
      @admin_route = Routes::Admin.new
      @health_route = Routes::Health.new
      @permissions_route = Routes::Permissions.new
    end

    def call(env)
      request = Rack::Request.new(env)

      catch(:halt) do
        case [request.request_method, request.path_info]
        when ["POST", "/auth/token"] then return @auth_route.call(request, @store, @token_service)
        when ["GET", "/me"] then return @me_route.call(request, @store, @token_service)
        when ["GET", "/users"] then return @users_route.index(request, @store, @token_service)
        when ["POST", "/users"] then return @users_route.create(request, @store, @token_service)
        when ["GET", "/groups"] then return @groups_route.index(request, @store, @token_service)
        when ["POST", "/groups"] then return @groups_route.create(request, @store, @token_service)
        when ["GET", "/permissions"] then return @permissions_route.call(request, @store, @token_service)
        when ["GET", "/admin/tenants"] then return @admin_route.index(request, @store, @token_service)
        when ["POST", "/admin/tenants"] then return @admin_route.create(request, @store, @token_service)
        when ["GET", "/health"] then return @health_route.call(request, @store, @token_service)
        end

        if request.get? && request.path_info.match?(%r{\A/users/[^/]+\z})
          user_id = request.path_info.split("/").last
          return @users_route.show(request, @store, @token_service, id: user_id)
        end

        if request.patch? && request.path_info.match?(%r{\A/users/[^/]+\z})
          user_id = request.path_info.split("/").last
          return @users_route.update(request, @store, @token_service, id: user_id)
        end

        if request.post? && request.path_info.match?(%r{\A/groups/[^/]+/permissions\z})
          group_id = request.path_info.split("/")[2]
          return @groups_route.assign_permission(request, @store, @token_service, id: group_id)
        end

        if request.post? && request.path_info.match?(%r{\A/groups/[^/]+/users\z})
          group_id = request.path_info.split("/")[2]
          return @groups_route.assign_user(request, @store, @token_service, id: group_id)
        end

        [404, { "Content-Type" => "application/json" }, [JSON.generate(error: "Not Found")]]
      end
    end
  end
end
