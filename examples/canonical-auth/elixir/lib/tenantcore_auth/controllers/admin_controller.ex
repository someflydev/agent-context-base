defmodule TenantcoreAuth.AdminController do
  use TenantcoreAuth, :controller

  def index(%Plug.Conn{assigns: %{auth: auth}} = conn, _params) do
    if auth.tenant_role == "super_admin" and "admin:tenant:create" in auth.permissions do
      tenants =
        TenantcoreAuth.Domain.InMemoryStore.list_tenants()
        |> Enum.map(fn tenant -> %{id: tenant.id, slug: tenant.slug, name: tenant.name} end)

      json(conn, %{tenants: tenants})
    else
      conn |> put_status(:forbidden) |> json(%{error: "Forbidden"})
    end
  end

  def create(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"slug" => slug, "name" => name, "first_admin_email" => email}) do
    if auth.tenant_role == "super_admin" and "admin:tenant:create" in auth.permissions do
      tenant = TenantcoreAuth.Domain.InMemoryStore.create_tenant(slug, name, email)
      conn |> put_status(:created) |> json(%{tenant: %{id: tenant.id, slug: tenant.slug, name: tenant.name}})
    else
      conn |> put_status(:forbidden) |> json(%{error: "Forbidden"})
    end
  end
end
