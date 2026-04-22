defmodule TenantcoreAuth.MeController do
  use TenantcoreAuth, :controller

  alias TenantcoreAuth.Domain.InMemoryStore
  alias TenantcoreAuth.Registry.RouteRegistry

  def show(%Plug.Conn{assigns: %{auth: auth}} = conn, _params) do
    user = InMemoryStore.get_user_by_id(auth.sub)
    tenant_id =
      case auth.tenant_id do
        value when value in [nil, "null", :null] -> nil
        ~c"null" -> nil
        value -> value
      end

    json(conn, %{
      sub: auth.sub,
      email: auth.email,
      display_name: user && user.display_name,
      tenant_id: tenant_id,
      tenant_name: tenant_id && InMemoryStore.get_tenant_name(tenant_id),
      tenant_role: auth.tenant_role,
      groups: auth.groups,
      permissions: auth.permissions,
      acl_ver: auth.acl_ver,
      allowed_routes:
        RouteRegistry.get_allowed_routes(auth)
        |> Enum.map(&Map.take(&1, [:method, :path, :permission, :description])),
      guide_sections: RouteRegistry.get_guide_sections(auth),
      issued_at: DateTime.to_iso8601(auth.issued_at),
      expires_at: DateTime.to_iso8601(auth.expires_at)
    })
  end

  def show(conn, _params) do
    conn |> put_status(:unauthorized) |> json(%{error: "Unauthorized"})
  end
end
