defmodule TenantcoreAuth.Router do
  use TenantcoreAuth, :router

  pipeline :public do
    plug :accepts, ["json"]
  end

  pipeline :authenticated do
    plug :accepts, ["json"]
    plug TenantcoreAuth.Auth.JwtPlug
  end

  scope "/", TenantcoreAuth do
    pipe_through :public

    post "/auth/token", AuthController, :token
    get "/health", HealthController, :index
  end

  scope "/", TenantcoreAuth do
    pipe_through :authenticated

    get "/me", MeController, :show
    get "/users", UserController, :index
    post "/users", UserController, :create
    get "/users/:id", UserController, :show
    patch "/users/:id", UserController, :update
    get "/groups", GroupController, :index
    post "/groups", GroupController, :create
    post "/groups/:id/permissions", GroupController, :assign_permission
    post "/groups/:id/users", GroupController, :assign_user
    get "/permissions", PermissionController, :index
  end

  scope "/admin", TenantcoreAuth do
    pipe_through :authenticated

    get "/tenants", AdminController, :index
    post "/tenants", AdminController, :create
  end
end
