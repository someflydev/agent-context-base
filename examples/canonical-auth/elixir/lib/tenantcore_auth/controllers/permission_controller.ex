defmodule TenantcoreAuth.PermissionController do
  use TenantcoreAuth, :controller

  plug TenantcoreAuth.Auth.RbacPlug, "iam:permission:read"

  def index(conn, _params) do
    permissions =
      TenantcoreAuth.Domain.InMemoryStore.list_permissions()
      |> Enum.map(fn permission -> %{id: permission.id, name: permission.name, description: permission.description} end)

    json(conn, %{permissions: permissions})
  end
end
